from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from shared import models, enums
from shared.database import SessionLocal, engine
from shared.utils.logger import get_logger
from shared.config import JUDGE_BATCH_SIZE

from api_llm.utils.memory import cleanup_ml_resources, clear_cuda_cache
from api_llm.judge.utils.error_handler import handle_judge_error
from api_llm.judge.inference import process_judge_batches
from api_llm.judge.model_loader import load_judge_base_model


logger = get_logger(__name__)


def run_judge_evaluation_task(judge_task_run_id: int) -> None:
    """
    Orchestrates the complete LLM-as-a-Judge evaluation lifecycle for a single run.

    This function isolates the Celery worker database connection, fetches the
    assigned task run, loads the specific judge model into VRAM, and processes
    the text generations in memory-safe batches. It persists the individual
    judge evaluations and cleans up GPU memory upon completion.

    Args:
        judge_task_run_id (int): The unique identifier of the JudgeTaskRun to process.
    """
    logger.info(f"Starting judge evaluation logic for run ID: {judge_task_run_id}")

    engine.dispose()

    model = None
    base_model = None
    tokenizer = None

    with SessionLocal() as db:
        try:
            run = db.query(models.JudgeTaskRun).filter(models.JudgeTaskRun.id == judge_task_run_id).first()
            if not run:
                logger.warning(f"[Judge Run {judge_task_run_id}] Not found in DB. Exiting.")
                return

            parent_task = run.evaluation_task

            if parent_task.status in (enums.TaskStatus.FAILED, enums.TaskStatus.CANCELLED):
                error_msg = f"Parent EvaluationTask {parent_task.id} ended with status: {parent_task.status.value}. Cancelling judge run."
                logger.warning(f"[Judge Run {judge_task_run_id}] {error_msg}")

                run.status = enums.TaskStatus.CANCELLED
                run.error_message = error_msg
                db.commit()
                return

            if parent_task.status != enums.TaskStatus.COMPLETED:
                logger.info(f"[Judge Run {judge_task_run_id}] Parent EvaluationTask {parent_task.id} is {parent_task.status.value}. Reverting judge to PENDING.")

                run.status = enums.TaskStatus.PENDING
                db.commit()
                return

            run.status = enums.TaskStatus.EVALUATING
            db.commit()

            generation_kwargs = run.judge_params or {}
            system_prompt = generation_kwargs.pop("system_prompt", "")
            model_name = run.judge.model_name

            logger.info(f"Loading judge model '{model_name}' into memory for task {judge_task_run_id}...")

            tokenizer, base_model, model = load_judge_base_model(
                model_name=model_name,
                load_params=generation_kwargs
            )

            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "left"

            process_judge_batches(
                db=db,
                judge_task_run_id=judge_task_run_id,
                evaluation_task_id=run.evaluation_task_id,
                judge_id=run.judge.id,
                model=model,
                tokenizer=tokenizer,
                system_prompt=system_prompt,
                generation_kwargs=generation_kwargs
            )

            run.status = enums.TaskStatus.COMPLETED
            run.completed_at = func.now()
            db.commit()

            logger.info(f"Judge run {judge_task_run_id} is fully COMPLETED.")

        except Exception as e:
            handle_judge_error(db, judge_task_run_id, e)

        finally:
            cleanup_ml_resources(model, base_model, tokenizer)
            clear_cuda_cache()