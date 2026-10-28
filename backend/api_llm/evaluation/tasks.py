import os
import shutil
import torch
from sqlalchemy.orm import Session

from shared import models, enums
from shared.database import SessionLocal
from shared.utils.logger import get_logger
from shared.datasets.dataset_downloader import download_dataset_if_needed
from api_llm.services.utils import prepare_prompts
from api_llm.models.loader_factory import load_evaluation_model
from api_llm.evaluation.inference_core import run_inference
from api_llm.evaluation.evaluator import calculate_multicriteria_profile
from api_llm.utils.memory import cleanup_ml_resources, clear_cuda_cache

logger = get_logger(__name__)


def _handle_task_error(db: Session, task_id: str, error: Exception) -> None:
    """
    Handles exceptions by logging the error, rolling back the database transaction,
    and updating the task status to FAILED.

    Args:
        db (Session): The active database session.
        task_id (str): The unique identifier of the evaluation task.
        error (Exception): The exception object that was raised during execution.
    """
    logger.warning(f"[Task {task_id}] ERROR during evaluation: {str(error)}", exc_info=True)

    db.rollback()

    db.query(models.EvaluationTask).filter(models.EvaluationTask.id == task_id).update({
        "status": enums.TaskStatus.FAILED,
        "error": str(error)
    })
    db.commit()


def _cleanup_disk_resources(task_id: str, temp_extract_dir: str | None) -> None:
    """
    Removes temporary extraction directories from the disk.
    """
    if temp_extract_dir and os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir, ignore_errors=True)
        logger.info(f"[Task {task_id}] Removed temp directory: {temp_extract_dir}")


def run_evaluation_task(task_id: str) -> None:
    """
    Orchestrates the background evaluation lifecycle for a specific LoRA adapter.

    This function manages the database state transitions, extracts the adapter ZIP
    to a temporary location, loads the models, triggers the inference process,
    and ensures all resources are properly cleaned up upon completion or failure.

    Args:
        task_id (str): The unique identifier of the evaluation task to execute.
    """
    db: Session = SessionLocal()
    temp_extract_dir = None
    model = None
    base_model = None
    tokenizer = None

    try:
        task = db.query(models.EvaluationTask).filter(models.EvaluationTask.id == task_id).first()
        if not task:
            logger.error(f"[Task {task_id}] Task not found in DB. Exiting.")
            return

        task.status = enums.TaskStatus.DOWNLOADING
        db.commit()

        download_dataset_if_needed(db, task)

        logger.info(f"[Task {task_id}] Delegating model loading to Factory...")
        tokenizer, base_model, model, temp_extract_dir = load_evaluation_model(task, db)

        task.status = enums.TaskStatus.PENDING
        db.commit()

        prompts_to_process = prepare_prompts(task, db)

        task.status = enums.TaskStatus.EVALUATING
        db.commit()

        logger.info(f"[Task {task_id}] Starting inference for the provided prompts stream")
        task_summary = run_inference(db, task, model, tokenizer, prompts_to_process)

        task.result = task_summary
        db.commit()

        logger.info(f"[Task {task.id}] Calculating multi-criteria profile...")
        metrics_record = calculate_multicriteria_profile(db=db, task_id=task.id)

        db.add(metrics_record)

        task.status = enums.TaskStatus.COMPLETED
        db.commit()
        logger.info(f"[Task {task_id}] Generation completed successfully")

    except Exception as e:
        _handle_task_error(db, task_id, e)
    finally:
        _cleanup_disk_resources(task_id, temp_extract_dir)

        cleanup_ml_resources(model, base_model, tokenizer)

        clear_cuda_cache()

        db.close()