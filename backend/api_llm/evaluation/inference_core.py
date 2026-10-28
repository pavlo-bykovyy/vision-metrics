import os
import time
import torch
from typing import Optional, Any, Iterator
from sqlalchemy.orm import Session
from transformers import PreTrainedTokenizerFast, BatchEncoding
from peft import PeftModel

from shared import models, enums
from shared.config import EVAL_BATCH_SIZE, DB_FLUSH_BATCH
from shared.utils.logger import get_logger

from api_llm.evaluation.result_builder import _parse_generation_outputs
from api_llm.evaluation.generation_utils import extract_clean_generated_text
from api_llm.services.utils import chunk_iterable, save_batch_to_db


logger = get_logger(__name__)


def generate_single_completion(
        model: PeftModel,
        tokenizer: PreTrainedTokenizerFast,
        messages: list[dict],
        generation_params: dict | None = None
) -> str:
    """
    Generates a text completion based on a sequence of chat messages.

    This is a universal function designed to handle both interactive chat streams
    and single-prompt queries. It prepares the generation parameters, applies
    the model's specific chat template, and processes the inference securely.

    Args:
        model (PeftModel): The loaded LoRA/PEFT model used for text generation.
        tokenizer (PreTrainedTokenizerFast): The tokenizer associated with the model.
        messages (list[dict]): A list of message dictionaries containing the conversation
            history (e.g., [{"role": "user", "content": "Hello!"}]).
        generation_params (dict | None, optional): Additional keyword arguments to control
            the text generation (e.g., max_tokens, temperature). Defaults to None.

    Returns:
        str: The newly generated text response, stripped of the original input prompt
        and any special control tokens.
    """
    params = generation_params or {}
    generation_kwargs = {**params}

    system_prompt = generation_kwargs.pop("system_prompt", None)

    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    generation_kwargs["pad_token_id"] = tokenizer.eos_token_id
    generation_kwargs["eos_token_id"] = tokenizer.eos_token_id

    temperature = generation_kwargs.get("temperature", 0.7)
    if temperature > 0:
        generation_kwargs["do_sample"] = True
    else:
        generation_kwargs["do_sample"] = False

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1536).to(model.device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            **generation_kwargs
        )

    raw_sequence = outputs.sequences[0] if hasattr(outputs, "sequences") else outputs[0]
    is_encoder_decoder = getattr(model.config, "is_encoder_decoder", False)
    clean_prompt = tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True).strip()

    generated_text, _ = extract_clean_generated_text(
        tokenizer=tokenizer,
        raw_sequence=raw_sequence,
        prompt_length=inputs.input_ids.shape[-1],
        is_encoder_decoder=is_encoder_decoder,
        clean_prompt=clean_prompt
    )

    return generated_text


def _prepare_batch_inputs(
        tokenizer: PreTrainedTokenizerFast,
        batch: list[dict[str, Any]],
        system_prompt: Optional[str],
        device: torch.device
) -> tuple[BatchEncoding, list[int]]:
    """
    Applies chat templates to a batch of prompts and tokenizes them.
    Dynamically maps dataset fields into the task's prompt template.

    Args:
        tokenizer (PreTrainedTokenizerFast): The tokenizer configured for the model.
        batch (list[dict[str, Any]]): A list of prompt dictionaries from prepare_prompts.
        system_prompt (Optional[str]): An optional system prompt to prepend to each message.
        device (torch.device): The hardware device (CPU/GPU) where tensors should be moved.

    Returns:
        tuple[BatchEncoding, list[int]]: The tokenized inputs and a list of token lengths.
    """
    if not batch:
        logger.warning("Received an empty batch in _prepare_batch_inputs.")
        return BatchEncoding(), []

    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    texts = []

    for item in batch:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        prompt_content = item.get("input_text", "")

        messages.append({
            "role": "user",
            "content": prompt_content
        })

        try:
            formatted_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            texts.append(formatted_text)
        except Exception as e:
            logger.warning(f"Error applying chat template: {e}. Falling back to raw prompt_content.")

            if system_prompt:
                texts.append(f"System: {system_prompt}\n\nUser: {prompt_content}\n\nAssistant:")
            else:
                texts.append(f"User: {prompt_content}\n\nAssistant:")

    inputs = tokenizer(
        texts, return_tensors="pt", padding=True, truncation=True, max_length=1536
    ).to(device)

    input_lengths = inputs.attention_mask.sum(dim=1).tolist()

    return inputs, input_lengths


def _get_stop_token_ids(tokenizer: PreTrainedTokenizerFast) -> list[int]:
    """
    Extracts standard End-Of-Sequence (EOS) tokens and model-specific chat terminators.
    This prevents the model from generating internal structural tokens (like <|system|>).

    Args:
        tokenizer (PreTrainedTokenizerFast): The tokenizer associated with the model.

    Returns:
        list[int]: A list of token IDs that should trigger the model to stop generating.
    """
    stop_token_ids = []

    if isinstance(tokenizer.eos_token_id, int):
        stop_token_ids.append(tokenizer.eos_token_id)
    elif isinstance(tokenizer.eos_token_id, list):
        stop_token_ids.extend(tokenizer.eos_token_id)

    chat_terminators = ["<|eot_id|>", "<|im_end|>", "<|system|>"]
    for token in chat_terminators:
        token_id = tokenizer.convert_tokens_to_ids(token)
        if token_id is not None and token_id != tokenizer.unk_token_id:
            stop_token_ids.append(token_id)

    return stop_token_ids


def _prepare_generation_kwargs(
        tokenizer: PreTrainedTokenizerFast,
        task_params: dict[str, Any]
) -> tuple[dict[str, Any], Optional[str]]:
    """
    Prepares the generation arguments for the model and configures tokenizer padding.

    Args:
        tokenizer (PreTrainedTokenizerFast): The tokenizer to configure.
        task_params (Dict[str, Any]): Generation parameters extracted from the task definition.

    Returns:
        tuple[dict[str, Any], Optional[str]]: A tuple containing the updated generation
        keyword arguments and the extracted system prompt (if any).
    """
    generation_kwargs = {**task_params}

    system_prompt = generation_kwargs.pop("system_prompt", None)

    stop_token_ids = _get_stop_token_ids(tokenizer)
    pad_token_id = stop_token_ids[0] if stop_token_ids else tokenizer.eos_token_id

    generation_kwargs.update({
        "pad_token_id": pad_token_id,
        "eos_token_id": stop_token_ids,
        "return_dict_in_generate": True,
        "output_scores": True,
        "do_sample": generation_kwargs.get("temperature", 0) > 0
    })

    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return generation_kwargs, system_prompt


def run_inference(
        db,
        task: models.EvaluationTask,
        model: PeftModel,
        tokenizer: PreTrainedTokenizerFast,
        prompts: Iterator[dict[str, Any]],
) -> str:
    """
    Executes batched text generation for a provided list of prompts and
    dynamically saves the results to the database in chunks to manage memory.

    Args:
        db (Session): The active database session.
        task (models.EvaluationTask): The evaluation task containing generation parameters.
        model (PeftModel): The configured PEFT/LoRA model ready for inference.
        tokenizer (PreTrainedTokenizerFast): The tokenizer associated with the model.
        prompts (Iterator[dict[str, str]]): A Iterator of dictionaries containing prompts to process.

    Returns:
        str: A summary message indicating the completion status and number of processed records.
    """
    results_to_save = []
    prompts_count = 0
    total_saved_records = 0

    task_params = task.generation_params or {}
    generation_kwargs, system_prompt = _prepare_generation_kwargs(tokenizer, task_params)

    logger.info(f"[Task {task.id}] Starting batched inference with batch_size={EVAL_BATCH_SIZE}.")

    with torch.inference_mode():
        for step, batch in enumerate(chunk_iterable(prompts, EVAL_BATCH_SIZE), start=1):

            db.refresh(task)

            if task.status == enums.TaskStatus.CANCELLED:
                logger.info(f"[Task {task.id}] Cancellation detected! Stopping inference at step {step}.")
                break

            logger.info(f"--- Processing Step {step} | Prompts processed so far: {prompts_count} ---")

            inputs, input_lengths = _prepare_batch_inputs(
                tokenizer, batch, system_prompt, model.device
            )

            start_time = time.time()
            logger.debug(f"Step {step}: Generating text...")

            outputs = model.generate(**inputs, **generation_kwargs)

            latency_time = time.time() - start_time
            logger.debug(f"Step {step}: Generation finished in {latency_time:.2f} seconds.")

            avg_latency = latency_time / len(batch)
            prompts_count += len(batch)

            batch_results = _parse_generation_outputs(
                task.id, tokenizer, batch, inputs, input_lengths, outputs, avg_latency, model
            )
            results_to_save.extend(batch_results)

            del inputs
            del outputs
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats(model.device)

            if len(results_to_save) >= DB_FLUSH_BATCH:
                records_count = len(results_to_save)
                is_saved = save_batch_to_db(db=db, records=results_to_save)

                if is_saved:
                    total_saved_records += records_count
                    logger.info(f"Step {step}: Successfully saved a batch of {records_count} records. Total saved: {total_saved_records}")
                else:
                    logger.warning(f"Step {step}: Failed to save {records_count} records. Dropped to free memory. Total saved remains: {total_saved_records}")

                results_to_save.clear()

    if results_to_save:
        records_count = len(results_to_save)
        is_saved = save_batch_to_db(db=db, records=results_to_save)

        if is_saved:
            total_saved_records += records_count
            logger.info(f"Successfully saved final batch of {records_count} records. Grand total saved: {total_saved_records}")
        else:
            logger.warning(f"Failed to save final {records_count} records.")

    return f"Success: Processed dataset with {prompts_count} prompts. Total successfully saved to DB: {total_saved_records}."
