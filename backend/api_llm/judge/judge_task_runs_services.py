from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from shared import schemas, models, enums
from shared.utils.logger import get_logger
from api_llm.judge.trigger_task import trigger_judge_task


logger = get_logger(__name__)


def get_evaluation_tasks_for_judge_ui(db: Session, size: int = 100) -> schemas.EvaluationTaskListResponse:
    """
    Retrieves evaluation tasks from the database and formats them for the UI dropdown.

    Args:
        db (Session): The active SQLAlchemy database session.
        size (int): The maximum number of tasks to retrieve. Defaults to 100.

    Returns:
        schemas.EvaluationTaskListResponse: A formatted list of evaluation tasks.
    """
    tasks = db.query(models.EvaluationTask) \
        .order_by(models.EvaluationTask.created_at.desc()) \
        .limit(size) \
        .all()

    result = []

    for task in tasks:
        status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)

        task_response = schemas.EvaluationTaskResponse(
            id=task.id,
            adapter_id=task.adapter_id,
            name=task.name,
            description=task.description,
            prompt_template=task.prompt_template,
            status=status_value,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at,
            adapter=task.adapter
        )
        result.append(task_response)

    return schemas.EvaluationTaskListResponse(tasks=result)

def create_judge_run(db: Session, payload: schemas.JudgeRunCreate) -> models.JudgeTaskRun:
    """
    Creates a new judge execution run (JudgeTaskRun) in the database.

    This method verifies the existence of both the specified evaluation task
    and the judge model. If validation passes, it persists the configuration
    for subsequent asynchronous execution.

    Args:
        db (Session): The active SQLAlchemy database session.
        payload (schemas.JudgeRunCreate): The data transfer object containing
            the evaluation task ID, judge ID, optional name/description, and
            specific generation parameters for the judge model.

    Returns:
        models.JudgeTaskRun: The newly created judge task run record with its
        initial status set to 'PENDING'.

    Raises:
        HTTPException: If the specified EvaluationTask is not found (404 Not Found).
        HTTPException: If the specified Judge model is not found (404 Not Found).
    """

    eval_task = db.query(models.EvaluationTask).filter(
        models.EvaluationTask.id == payload.evaluation_task_id
    ).first()

    if not eval_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation task with ID {payload.evaluation_task_id} not found."
        )

    judge = db.query(models.Judge).filter(
        models.Judge.id == payload.judge_id
    ).first()

    if not judge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Judge with ID {payload.judge_id} not found."
        )

    new_judge_run = models.JudgeTaskRun(
        evaluation_task_id=payload.evaluation_task_id,
        judge_id=payload.judge_id,
        name=payload.name,
        description=payload.description,
        judge_params=payload.judge_params,
        status=enums.TaskStatus.PENDING
    )

    db.add(new_judge_run)
    db.commit()
    db.refresh(new_judge_run)

    try:
        celery_task_id = trigger_judge_task(new_judge_run.id)

        new_judge_run.celery_task_id = celery_task_id
        db.commit()

    except RuntimeError as e:
        new_judge_run.status = enums.TaskStatus.FAILED
        new_judge_run.error_message = str(e)
        db.commit()
        raise

    return new_judge_run

def get_paginated_judge_runs(db: Session, page: int = 1, size: int = 20):
    """
    Fetches a paginated list of JudgeTaskRuns ordered by newest first.
    """
    skip = (page - 1) * size
    total = db.query(models.JudgeTaskRun).count()

    items = (
        db.query(models.JudgeTaskRun)
        .order_by(models.JudgeTaskRun.created_at.desc())
        .offset(skip)
        .limit(size)
        .all()
    )

    pages = (total + size - 1) // size

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }

def cancel_judge_run(db: Session, run_id: int, user_id: int = None) -> models.JudgeTaskRun:
    """
    Cancels an ongoing background judge task run and updates its status.

    This service method retrieves the judge task run from the database, validates
    that it is in a cancellable state, stops the associated Celery worker (if applicable),
    and updates the database record to reflect the 'CANCELLED' status.

    Args:
        db (Session): The active SQLAlchemy database session.
        run_id (int): The unique identifier of the judge task run to cancel.
        user_id (int, optional): The ID of the user requesting the cancellation, used for logging.

    Raises:
        ValueError: If the task is not found, lacks a Celery ID, or is already completed/failed/cancelled.

    Returns:
        models.JudgeTaskRun: The updated judge task run record.
    """
    db_run = db.query(models.JudgeTaskRun).filter(models.JudgeTaskRun.id == run_id).first()

    if not db_run:
        raise ValueError("Judge task run not found")

    if not hasattr(db_run, 'celery_task_id') or not db_run.celery_task_id:
        raise ValueError("Cannot cancel: No running Celery task found for this judge run.")

    terminal_statuses = [
        enums.TaskStatus.COMPLETED,
        enums.TaskStatus.FAILED,
        enums.TaskStatus.CANCELLED
    ]

    if db_run.status in terminal_statuses:
        raise ValueError(f"Cannot cancel task. Current status is {db_run.status}")

    db_run.status = enums.TaskStatus.CANCELLED
    db.commit()
    db.refresh(db_run)

    logger.info(f"Judge task run {run_id} was cancelled (Requested by user ID: {user_id})")

    return db_run


def delete_judge_run(db: Session, run_id: int, user_id: int = None) -> dict:
    """
    Deletes a judge task run from the database.

    Args:
        db (Session): The active SQLAlchemy database session.
        run_id (int): The unique identifier of the judge task run to delete.
        user_id (int, optional): The ID of the user requesting the deletion, used for logging.

    Raises:
        ValueError: If the task is not found or is currently running.

    Returns:
        dict: A confirmation message.
    """
    db_run = db.query(models.JudgeTaskRun).filter(models.JudgeTaskRun.id == run_id).first()

    if not db_run:
        raise ValueError("Judge task run not found")

    db.delete(db_run)
    db.commit()

    logger.info(f"Judge task run {run_id} was deleted (Requested by user ID: {user_id})")

    return {"detail": "Task run successfully deleted"}