import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from shared import models, schemas, enums
from shared.utils.logger import get_logger
from api_llm.services.evaluation_service import trigger_evaluation_task

class TaskNotFoundError(Exception):
    pass

class TaskCancelError(Exception):
    pass


logger = get_logger(__name__)


def _process_and_dispatch_task(
        db,
        task: "models.EvaluationTask"
) -> dict:
    """
    Persists the evaluation task to the database, initializes judge task runs if provided,
    and dispatches the workflow to the Celery queue.

    Args:
        db: The database session instance.
        task (models.EvaluationTask): The evaluation task instance to be saved.

    Returns:
        dict: A dictionary containing the generated evaluation task ID.

    Raises:
        HTTPException: If a database integrity error or a general SQLAlchemy error occurs.
    """
    try:
        judge_run_ids = [jr.id for jr in task.judge_runs]

        task_data = trigger_evaluation_task(
            evaluation_task_id=task.id,
            judge_task_run_ids=judge_run_ids
        )

        task.celery_task_id = task_data.main_task_id

        if judge_run_ids and hasattr(task_data, 'judge_task_ids'):
            for judge_run in task.judge_runs:
                judge_run.celery_task_id = task_data.judge_task_ids.get(judge_run.id)

        db.commit()

        return {"task_id": task.id}

    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Database integrity error (IntegrityError): {e.orig}")
        raise HTTPException(
            status_code=400,
            detail="Database constraint error: Check if related IDs (adapter, dataset, etc.) exist."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.warning(f"General database error (SQLAlchemyError): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save task to the database. Check server logs."
        )


def create_evaluation_task(request: schemas.EvaluateRequest, db) -> dict:
    """
    Validates the incoming request and creates a new LoRA evaluation task.

    Args:
        request (schemas.EvaluateRequest): The request payload containing evaluation parameters.
        db: The database session instance.

    Returns:
        dict: A dictionary containing a success message and the created task ID.

    Raises:
        HTTPException: If the specified adapter or dataset is not found in the database.
    """
    adapter = db.query(models.LoraAdapter).filter(models.LoraAdapter.id == request.adapter_id).first()
    if not adapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Adapter {request.adapter_id} not found.")

    if request.dataset_id:
        dataset = db.query(models.Dataset).filter(models.Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {request.dataset_id} not found.")

    if request.judge_ids:
        found_judges_count = db.query(models.Judge).filter(models.Judge.id.in_(request.judge_ids)).count()
        if found_judges_count != len(set(request.judge_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more specified judges were not found."
            )

    judge_run_objects = []
    if request.judge_ids:
        for judge_id in request.judge_ids:
            judge_run_objects.append(
                models.JudgeTaskRun(
                    judge_id=judge_id,
                    name=f"{request.name or 'Evaluation'} - Judge {judge_id}",
                    status=TaskStatus.PENDING
                )
            )

    task = models.EvaluationTask(
        name=request.name,
        description=request.description,
        adapter_id=request.adapter_id,
        dataset_id=request.dataset_id,
        base_model_to_use=request.base_model_id,
        prompt=request.prompt,
        generation_params=request.generation_params,
        evaluation_type=enums.EvaluationType.LORA,
        judge_runs=judge_run_objects
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    result = _process_and_dispatch_task(db, task)

    return {
        "message": "Evaluation task and judge runs created successfully",
        "task_id": result["task_id"]
    }


def create_base_model_evaluation_task(request: schemas.EvaluateRequest, db) -> dict:
    """
    Validates the incoming request and creates a new base model evaluation task,
    along with associated judge task runs if provided.

    Args:
        request (schemas.EvaluateRequest): The request payload containing evaluation parameters.
        db: The database session instance.

    Returns:
        dict: A dictionary containing a success message and the created task ID.

    Raises:
        HTTPException: If the base model ID is missing, or if the dataset/judges are not found.
    """
    if not request.base_model_id:
        raise HTTPException(status_code=400, detail="base_model_id is required for Base Model evaluation.")

    if request.dataset_id:
        dataset = db.query(models.Dataset).filter(models.Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_id} not found.")

    if request.judge_ids:
        found_judges_count = db.query(models.Judge).filter(models.Judge.id.in_(request.judge_ids)).count()
        if found_judges_count != len(set(request.judge_ids)):
            raise HTTPException(
                status_code=404,
                detail="One or more specified judges were not found."
            )

    judge_run_objects = []
    if request.judge_ids:
        for judge_id in request.judge_ids:
            judge_run_objects.append(
                models.JudgeTaskRun(
                    judge_id=judge_id,
                    name=f"{request.name or 'Base Model Eval'} - Judge {judge_id}",
                    status=TaskStatus.PENDING
                )
            )

    task = models.EvaluationTask(
        name=request.name,
        description=request.description,
        adapter_id=None,
        dataset_id=request.dataset_id,
        base_model_to_use=request.base_model_id,
        prompt=request.prompt,
        generation_params=request.generation_params,
        evaluation_type=enums.EvaluationType.BASE_MODEL,
        judge_runs=judge_run_objects
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    result = _process_and_dispatch_task(db, task)

    return {
        "message": "Base Model evaluation task and judge runs created successfully",
        "task_id": result["task_id"]
    }


def cancel_evaluation_task(db: Session, evaluation_task_id: int, user_id: int = None) -> models.EvaluationTask:
    """
    Cancels an ongoing background evaluation task and updates its status.

    This service method retrieves the evaluation from the database, validates
    that it is in a cancellable state, stops the associated Celery worker,
    and updates the database record to reflect the 'CANCELLED' status.

    Args:
        db (Session): The active SQLAlchemy database session.
        evaluation_task_id (int): The unique identifier of the evaluation to cancel.
        user_id (int, optional): The ID of the user requesting the cancellation, used for logging.

    Raises:
        ValueError: If the evaluation is not found, lacks a Celery ID, or is already completed/failed/cancelled.

    Returns:
        models.Evaluation: The updated evaluation record.
    """
    db_eval = db.query(models.EvaluationTask).filter(models.EvaluationTask.id == evaluation_task_id).first()

    if not db_eval:
        raise TaskNotFoundError("Evaluation not found.")

    terminal_statuses = [
        enums.TaskStatus.COMPLETED,
        enums.TaskStatus.FAILED,
        enums.TaskStatus.CANCELLED
    ]
    if db_eval.status in terminal_statuses:
        raise TaskCancelError(f"Cannot cancel task. Current status is {db_eval.status.name}")

    db_eval.status = enums.TaskStatus.CANCELLED
    db.commit()
    db.refresh(db_eval)

    logger.info(f"Evaluation {evaluation_task_id} was cancelled (Requested by user ID: {user_id})")

    return db_eval

def delete_task_record(db: Session, task_id: int):
    """
    Retrieves a task by ID, cancels its background process if it is still running,
    and then deletes it from the database.
    """
    task = db.query(models.EvaluationTask).filter(models.EvaluationTask.id == task_id).first()

    if not task:
        raise TaskNotFoundError("Evaluation task not found.")

    active_statuses = [
        enums.TaskStatus.PENDING,
        enums.TaskStatus.DOWNLOADING,
        enums.TaskStatus.EVALUATING
    ]

    if task.status in active_statuses:
        task.status = enums.TaskStatus.CANCELLED

        db.commit()

        return {"message": f"Task {task_id} is in progress, stop request sent"}

    try:
        db.delete(task)
        db.commit()

        return {"message": f"Task {task_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete task from database: {str(e)}")