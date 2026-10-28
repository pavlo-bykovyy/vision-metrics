from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shared import models, schemas
from api_cv.services import services
from shared.database import get_db
from shared.dependencies import verify_token
from shared.utils.logger import get_logger


logger = get_logger("EVALUATION-ROUTER")

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@router.get("/", response_model=schemas.EvaluationPaginationResponse)
def get_evaluations(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1, description="Page number for pagination"),
        size: int = Query(10, ge=1, le=100, description="Number of items per page"),
        current_user: dict = Depends(verify_token)
):
    """
    Retrieve a paginated list of all model evaluations.

    This endpoint fetches a list of evaluation records, ordered by their creation
    date (newest first). It leverages the database model to efficiently load
    both the evaluation metadata and the associated performance metrics.

    Returns:
        EvaluationPaginationResponse: A structured model containing the list of
        evaluations and pagination metadata (total items, current page, etc.).
    """
    items, total, pages = models.Evaluation.get_paginated(db, page, size)

    return schemas.EvaluationPaginationResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{evaluation_id}", response_model=schemas.EvaluationDetail)
def get_evaluation(
        evaluation_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Retrieve detailed information for a specific evaluation.

    This endpoint looks up a single evaluation by its unique identifier.
    It includes all related data, such as the status, error messages, and
    calculated metrics (e.g., accuracy, F1 score).

    Args:
        evaluation_id (int): The unique identifier of the evaluation.

    Raises:
        HTTPException: 404 error if the evaluation is not found in the database.

    Returns:
        EvaluationDetail: A structured model containing the full evaluation details.
    """
    db_eval = models.Evaluation.get_by_id(db, evaluation_id)

    if not db_eval:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return db_eval


@router.delete("/{evaluation_id}")
def delete_evaluation(
        evaluation_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Delete a specific evaluation record from the database.

    This endpoint removes the evaluation and its cascading associated data
    (like metrics) from the system.

    Args:
        evaluation_id (int): The unique identifier of the evaluation to delete.

    Raises:
        HTTPException: 404 error if the evaluation does not exist.

    Returns:
        dict: A success message confirming the deletion.
    """
    success = models.Evaluation.delete_by_id(db, evaluation_id)

    if not success:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return {"message": f"Evaluation {evaluation_id} successfully deleted"}


@router.post("/create", response_model=schemas.Evaluation)
async def run_evaluation(
        request: schemas.EvaluateModelRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Create and start a new evaluation task for a specific model.

    This endpoint takes a model ID and a dataset ID, creates a new Evaluation
    record with a 'PENDING' status, and triggers the machine learning
    evaluation script in the background. This ensures the API remains fast
    and responsive.

    Args:
        request (schemas.EvaluateModelRequest): The payload containing the target dataset_id.
        db (Session, optional): The database session dependency.
        current_user (dict, optional): The authenticated user information.

    Returns:
        schemas.Evaluation: The newly created evaluation record containing its ID and initial status.
    """
    return services.create_evaluation_task(
        db=db,
        model_id=request.model_id,
        dataset_id=request.dataset_id
    )


@router.post("/{evaluation_id}/re-evaluate", response_model=schemas.Evaluation)
async def re_evaluate_model(
        evaluation_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Trigger a re-evaluation based on a previous evaluation record.

    This endpoint initiates a new background task to evaluate the model again
    against the exact same dataset used in the specified past evaluation.
    It does not overwrite the old data; instead, it generates a completely
    new Evaluation record linked to the same model and dataset.

    Args:
        evaluation_id (int): The unique identifier of the previous evaluation to duplicate.
        db (Session, optional): The database session dependency.
        current_user (dict, optional): The authenticated user information.

    Returns:
        schemas.Evaluation: The newly generated evaluation record for the current run.
    """
    return services.re_evaluate_task(db=db, evaluation_id=evaluation_id)


@router.post("/{evaluation_id}/cancel")
def cancel_evaluation(
        evaluation_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Cancel an ongoing background evaluation task.

    This endpoint forcefully terminates the background process associated
    with the given evaluation ID and updates its status to CANCELLED in the database.

    Args:
        evaluation_id (int): The unique identifier of the evaluation to cancel.
        db (Session): The database session dependency.
        current_user (dict): The authenticated user information.

    Raises:
        HTTPException: 404 error if the evaluation is not found.
        HTTPException: 400 error if the task is already finished or has no Celery ID.

    Returns:
        dict: A success message confirming the task was cancelled.
    """
    try:
        services.cancel_evaluation_task(
            db=db,
            evaluation_id=evaluation_id,
            user_id=current_user.get('id')
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Evaluation not found":
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

    return {"message": f"Evaluation {evaluation_id} has been successfully cancelled."}

