from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from shared import schemas, models, enums
from shared.dependencies import verify_token
from shared.database import get_db
from shared.utils.logger import get_logger

from api_llm.services.service import (
    create_base_model_evaluation_task,
    cancel_evaluation_task,
    delete_task_record,
    TaskNotFoundError,
    TaskCancelError
)
from api_llm.services.evaluation_results_service import get_paginated_evaluation_results


logger = get_logger(__name__)

router = APIRouter(prefix="/base-models/evaluations", tags=["Base Model Evaluations"])


@router.get("/", response_model=schemas.EvaluationTaskListResponse)
def get_all_base_evaluations(
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Retrieves all BASE MODEL evaluation tasks from the database."""
    tasks = db.query(models.EvaluationTask) \
        .filter(models.EvaluationTask.evaluation_type == enums.EvaluationType.BASE_MODEL) \
        .order_by(models.EvaluationTask.created_at.desc()) \
        .all()

    result = []
    for task in tasks:
        status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)

        task_response = schemas.EvaluationTaskResponse(
            id=task.id,
            adapter_id=task.adapter_id,
            name=task.name,
            description=task.description,
            status=status_value,
            result=task.result,
            error_message=task.error_message,
            created_at=task.created_at,
            adapter=None
        )
        result.append(task_response)

    return schemas.EvaluationTaskListResponse(tasks=result)


@router.post("/")
async def start_base_evaluation(
        request: schemas.EvaluateRequest,
        db: Session = Depends(get_db)
):
    """Initializes a background task for Base Model evaluation."""
    return create_base_model_evaluation_task(request=request, db=db)


@router.get("/{task_id}", response_model=schemas.EvaluationTaskResponse)
async def get_evaluation_status(
        task_id: str,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Get the current status of an evaluation task."""
    task = db.query(models.EvaluationTask) \
        .options(joinedload(models.EvaluationTask.metrics)) \
        .filter(models.EvaluationTask.id == task_id) \
        .first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)

    return schemas.EvaluationTaskResponse(
        id=task.id,
        adapter_id=task.adapter_id,
        name=task.name,
        description=task.description,
        status=status_value,
        result=task.result,
        error_message=task.error_message,
        created_at=task.created_at,
        metrics=task.metrics
    )


@router.post("/{task_id}/cancel")
def cancel_evaluation(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Cancel an ongoing background evaluation task.

    This endpoint forcefully terminates the background process associated
    with the given evaluation ID and updates its status to CANCELLED in the database.

    Args:
        task_id (int): The unique identifier of the evaluation to cancel.
        db (Session): The database session dependency.
        current_user (dict): The authenticated user information.

    Raises:
        HTTPException: 404 error if the evaluation is not found.
        HTTPException: 400 error if the task is already finished or has no Celery ID.

    Returns:
        dict: A success message confirming the task was cancelled.
    """
    try:
        cancel_evaluation_task(
            db=db,
            evaluation_task_id=task_id,
            user_id=current_user.get('id')
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaskCancelError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": f"Evaluation task {task_id} has been successfully cancelled."}


@router.delete("/{task_id}")
async def delete_evaluation_task(
        task_id: str,
        db: Session = Depends(get_db)
):
    """
        Deletes an evaluation task from the database.
        If the task is currently running, it will gracefully cancel the background process first.
        """
    try:
        return delete_task_record(db=db, task_id=task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/results", response_model=schemas.EvaluationResultPaginationResponse)
async def get_evaluation_results(
        task_id: int,
        page: int = 1,
        size: int = 100,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """
    Retrieves the generated text results for a specific evaluation task.
    Supports standard pagination (page and size) to handle large datasets.
    """
    return get_paginated_evaluation_results(
        task_id=task_id,
        page=page,
        size=size,
        db=db
    )