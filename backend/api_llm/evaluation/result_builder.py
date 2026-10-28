from typing import Any, Optional
import torch
from transformers import PreTrainedTokenizerFast, BatchEncoding
from peft import PeftModel

from shared import models

from api_llm import dtos
from api_llm.evaluation.generation_utils import extract_clean_generated_text


def _calculate_avg_logprob(seq_scores: Optional[torch.Tensor]) -> float:
    """
    Calculates the average logarithmic probability from the generated sequence scores.

    Args:
        seq_scores (Optional[torch.Tensor]): A tensor containing transition scores
            for each generated token. Can be None if scores are not outputted by the model.

    Returns:
        float: The mean of the valid (non-infinite, non-NaN) log probabilities.
        Returns 0.0 if scores are None or invalid.
    """
    if seq_scores is None:
        return 0.0

    valid_scores = seq_scores[~torch.isinf(seq_scores) & ~torch.isnan(seq_scores)]
    if len(valid_scores) > 0:
        return valid_scores.mean().item()

    return 0.0


def _build_metadata(
        is_encoder_decoder: bool,
        generated_tokens_count: int,
        raw_prompt_text: str,
        inputs_dict: dict
) -> dict:
    """
    Constructs a metadata dictionary containing additional generation details
    to be stored in the database.

    Args:
        is_encoder_decoder (bool): True if the model is an encoder-decoder, False if decoder-only.
        generated_tokens_count (int): The total number of newly generated tokens.
        raw_prompt_text (str): The decoded text of the original prompt (used for debugging).
        inputs_dict (dict): The original input fields extracted from the dataset.

    Returns:
        dict: A structured dictionary containing the execution metadata.
    """
    return {
        "model_architecture": "encoder-decoder" if is_encoder_decoder else "decoder-only",
        "total_tokens_generated": generated_tokens_count,
        "debug_raw_prompt": raw_prompt_text,
        "inputs": inputs_dict
    }


def _create_evaluation_result(
        task_id: int,
        tokenizer: PreTrainedTokenizerFast,
        item: dict[str, Any],
        context: dtos.GenerationContext
) -> models.EvaluationResult:
    """
    Processes a single generated sequence and constructs an EvaluationResult database record.

    Args:
        task_id (int): The unique identifier of the evaluation task.
        tokenizer (PreTrainedTokenizerFast): The tokenizer used for decoding sequences.
        item (dict[str, Any]): The original dataset item containing the prompt ID and input text.
        context (dtos.GenerationContext): An object containing all relevant metrics and tensors
            for this specific generation step.

    Returns:
        models.EvaluationResult: The populated database model ready to be saved.
    """
    clean_prompt = item["input_text"].strip()

    generated_text, generated_tokens_count = extract_clean_generated_text(
        tokenizer=tokenizer,
        raw_sequence=context.raw_output_seq,
        prompt_length=context.padded_input_len,
        is_encoder_decoder=context.is_encoder_decoder,
        clean_prompt=clean_prompt
    )

    raw_prompt_text = tokenizer.decode(
        context.input_ids_seq[:context.prompt_tokens_count],
        skip_special_tokens=False
    )

    avg_logprob_val = _calculate_avg_logprob(context.seq_scores)

    metadata_dict = _build_metadata(
        context.is_encoder_decoder,
        generated_tokens_count,
        raw_prompt_text,
        item.get("inputs", {})
    )

    return models.EvaluationResult(
        task_id=task_id,
        prompt_id=item["prompt_id"],
        input_text=item["input_text"],
        generated_text=generated_text,
        prompt_tokens=context.prompt_tokens_count,
        completion_tokens=generated_tokens_count,
        latency_seconds=context.avg_latency,
        avg_logprob=avg_logprob_val,
        peak_memory_mb=context.peak_memory_mb,
        metadata_=metadata_dict
    )


def _parse_generation_outputs(
        task_id: int,
        tokenizer: PreTrainedTokenizerFast,
        batch: list[dict[str, Any]],
        inputs: BatchEncoding,
        input_lengths: list[int],
        outputs: Any,
        avg_latency: float,
        model: PeftModel,
) -> list[models.EvaluationResult]:
    """
    Iterates over a batch of model outputs and constructs database records for the results.

    Args:
        task_id (int): The unique identifier of the evaluation task.
        tokenizer (PreTrainedTokenizerFast): The tokenizer used to decode the outputs.
        batch (list[dict[str, Any]]): The original batch of prompt dictionaries.
        inputs (BatchEncoding): The original tokenized inputs (used to slice output sequences).
        input_lengths (list[int]): The token counts of the input prompts.
        outputs (Any): The raw generation output object from the Hugging Face model.
        avg_latency (float): The calculated average latency per prompt in seconds.
        model (PeftModel): The configured PEFT/LoRA model ready for inference.

    Returns:
        list[models.EvaluationResult]: A list of formatted results ready to be saved.
    """
    parsed_results = []
    is_encoder_decoder = getattr(model.config, "is_encoder_decoder", False)

    transition_scores = None
    if hasattr(outputs, "scores"):
        transition_scores = model.compute_transition_scores(
            outputs.sequences, outputs.scores, normalize_logits=True
        )

    peak_memory_mb = 0.0
    if torch.cuda.is_available():
        peak_memory_mb = torch.cuda.max_memory_allocated(model.device) / (1024 ** 2)

    padded_input_len = inputs.input_ids.shape[1]

    for i, item in enumerate(batch):
        seq_scores = transition_scores[i] if transition_scores is not None else None

        context = dtos.GenerationContext(
            input_ids_seq=inputs.input_ids[i],
            padded_input_len=padded_input_len,
            prompt_tokens_count=input_lengths[i],
            raw_output_seq=outputs.sequences[i],
            seq_scores=seq_scores,
            avg_latency=avg_latency,
            peak_memory_mb=peak_memory_mb,
            is_encoder_decoder=is_encoder_decoder
        )

        result_record = _create_evaluation_result(
            task_id=task_id,
            tokenizer=tokenizer,
            item=item,
            context=context
        )

        parsed_results.append(result_record)

    return parsed_results
