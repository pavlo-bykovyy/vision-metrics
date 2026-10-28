import torch
import logging
from sqlalchemy.orm import Session

from shared import models
from api_llm.judge.utils.promt_utils import format_judge_prompt, parse_judge_json


logger = logging.getLogger(__name__)

JUDGE_BATCH_SIZE = 16


def process_judge_batches(
        db: Session,
        judge_task_run_id: int,
        evaluation_task_id: int,
        judge_id: int,
        model,
        tokenizer,
        system_prompt: str,
        generation_kwargs: dict
) -> None:
    """
    Executes batched LLM-as-a-Judge inference and saves scores to the database.
    Manages VRAM safely by explicitly deleting tensors.
    """
    offset = 0

    while True:
        results_batch = (
            db.query(models.EvaluationResult)
            .filter(models.EvaluationResult.task_id == evaluation_task_id)
            .order_by(models.EvaluationResult.id)
            .offset(offset)
            .limit(JUDGE_BATCH_SIZE)
            .all()
        )

        if not results_batch:
            break

        logger.info(f"Processing judge batch: records {offset} to {offset + len(results_batch)}")

        judge_prompts = [
            format_judge_prompt(system_prompt, res.input_text, res.generated_text)
            for res in results_batch
        ]

        with torch.inference_mode():
            inputs = tokenizer(
                judge_prompts,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(model.device)

            outputs = model.generate(**inputs, **generation_kwargs)

            input_lengths = inputs['input_ids'].shape[1]
            decoded_responses = tokenizer.batch_decode(outputs[:, input_lengths:], skip_special_tokens=True)

            del inputs
            del outputs
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        for result, judge_output in zip(results_batch, decoded_responses):
            scores = parse_judge_json(judge_output)

            judge_eval = models.JudgeEvaluation(
                result_id=result.id,
                judge_model_id=judge_id,
                judge_task_run_id=judge_task_run_id,
                safety_score=scores.get("safety", 0.0),
                accuracy_score=scores.get("accuracy", 0.0),
                hallucination_score=scores.get("hallucination", 0.0),
                reasoning=scores.get("reasoning", "Failed to parse judge reasoning.")
            )
            db.add(judge_eval)

        db.commit()
        offset += JUDGE_BATCH_SIZE