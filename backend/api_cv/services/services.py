import datetime
import os
import math
import shutil
import asyncio
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import joinedload, Session

from shared.config import UPLOAD_DIR
from shared.services.evaluation_queue_service import trigger_evaluation_task
from shared import models, enums
from shared.utils.logger import get_logger
import traceback


logger = get_logger(__name__)


def create_evaluation_record(db: Session, model_id: int, dataset_id: int) -> models.Evaluation:
    """
    Validates the requested model and dataset, and creates a new evaluation record.

    Args:
        db (Session): The active SQLAlchemy database session.
        model_id (int): The unique identifier of the model to be evaluated.
        dataset_id (int): The unique identifier of the dataset used for evaluation.

    Returns:
        models.Evaluation: The newly created evaluation record with a 'PENDING' status.

    Raises:
        HTTPException: Raises a 404 error if the specified model is not found in the database.
        HTTPException: Raises a 404 error if the specified dataset is not found in the database.
    """
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    db_dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    new_evaluation = models.Evaluation(
        model_id=model_id,
        dataset_id=dataset_id,
        status=enums.TaskStatus.PENDING
    )
    db.add(new_evaluation)
    db.commit()
    db.refresh(new_evaluation)

    return new_evaluation


def create_evaluation_task(db: Session, model_id: int, dataset_id: int):
    """
    Creates a new evaluation record and triggers the background evaluation process.

    Args:
        db (Session): The active SQLAlchemy database session.
        model_id (int): The unique identifier of the model to be evaluated.
        dataset_id (int): The unique identifier of the dataset used for evaluation.

    Returns:
        models.Evaluation: The newly created evaluation record.
    """
    logger.info(f"Starting evaluation task creation for model_id={model_id}, dataset_id={dataset_id}")

    try:
        new_evaluation = create_evaluation_record(db, model_id, dataset_id)
        logger.info(f"Successfully created evaluation record in database. Evaluation ID: {new_evaluation.id}")

        celery_task_id = trigger_evaluation_task(evaluation_id=new_evaluation.id)

        new_evaluation.celery_task_id = celery_task_id
        db.commit()
        db.refresh(new_evaluation)

        return new_evaluation

    except Exception as e:
        logger.warning(
            f"Failed to create evaluation task for model_id={model_id}, dataset_id={dataset_id}. Error: {str(e)}",
            exc_info=True
        )
        raise e


def re_evaluate_task(db: Session, evaluation_id: int) -> models.Evaluation:
    """
    Fetches an existing evaluation and triggers a new one using the same model and dataset.

    Args:
        db (Session): The active SQLAlchemy database session.
        evaluation_id (int): The unique identifier of the previous evaluation record.

    Returns:
        models.Evaluation: The newly created evaluation record for the current run.

    Raises:
        HTTPException: Raises a 404 error if the previous evaluation record is not found.
    """
    old_evaluation = models.Evaluation.get_by_id(db, evaluation_id)

    if not old_evaluation:
        raise HTTPException(status_code=404, detail="Previous evaluation not found.")

    return create_evaluation_task(db, old_evaluation.model_id, old_evaluation.dataset_id)


def save_upload_file(upload_file: UploadFile) -> tuple:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return new_filename, file_path
    except Exception as e:
        logger.warning(f"Save error: {e}")
        raise RuntimeError(f"Storage error: {e}")
    finally:
        upload_file.file.close()


def cancel_evaluation_task(db: Session, evaluation_id: int, user_id: int = None) -> models.Evaluation:
    """
    Cancels an ongoing background evaluation task and updates its status.

    This service method retrieves the evaluation from the database, validates
    that it is in a cancellable state, stops the associated Celery worker,
    and updates the database record to reflect the 'CANCELLED' status.

    Args:
        db (Session): The active SQLAlchemy database session.
        evaluation_id (int): The unique identifier of the evaluation to cancel.
        user_id (int, optional): The ID of the user requesting the cancellation, used for logging.

    Raises:
        ValueError: If the evaluation is not found, lacks a Celery ID, or is already completed/failed/cancelled.

    Returns:
        models.Evaluation: The updated evaluation record.
    """
    db_eval = models.Evaluation.get_by_id(db, evaluation_id)

    if not db_eval:
        raise ValueError("Evaluation not found")

    if not hasattr(db_eval, 'celery_task_id') or not db_eval.celery_task_id:
        raise ValueError("Cannot cancel: No running Celery task found for this evaluation.")

    terminal_statuses = [
        enums.TaskStatus.COMPLETED,
        enums.TaskStatus.FAILED,
        enums.TaskStatus.CANCELLED
    ]
    if db_eval.status in terminal_statuses:
        raise ValueError(f"Cannot cancel task. Current status is {db_eval.status}")

    db_eval.status = enums.TaskStatus.CANCELLED
    db.commit()
    db.refresh(db_eval)

    logger.info(f"Evaluation {evaluation_id} was cancelled (Requested by user ID: {user_id})")

    return db_eval

