import math
from fastapi import HTTPException
from sqlalchemy.orm import Session
from shared import models, schemas


def get_paginated_evaluation_results(
        task_id: int,
        page: int,
        size: int,
        db: Session
) -> schemas.EvaluationResultPaginationResponse:
    """
    Retrieves a paginated list of evaluation results for a specific task.

    This function verifies that the evaluation task exists, calculates the
    required offset based on the requested page and size, and fetches the
    corresponding slice of results from the database.

    Args:
        task_id (int): The unique identifier of the parent evaluation task.
        page (int): The requested page number (1-indexed). If a value less
            than 1 is provided, it defaults to 1.
        size (int): The maximum number of result records to return per page.
        db (Session): The active SQLAlchemy database session.

    Returns:
        schemas.EvaluationResultPaginationResponse: A Pydantic model containing
        the paginated items and metadata (total count, current page, page size,
        and total pages).

    Raises:
        HTTPException: Raises a 404 error if the specified task_id does not
        exist in the evaluation_tasks table.
    """
    task = db.query(models.EvaluationTask).filter(models.EvaluationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Evaluation task not found")

    query = db.query(models.EvaluationResult).filter(models.EvaluationResult.task_id == task_id)

    total_count = query.count()
    total_pages = math.ceil(total_count / size) if total_count > 0 else 0

    current_page = max(1, page)
    skip = (current_page - 1) * size

    results = query.order_by(models.EvaluationResult.id).offset(skip).limit(size).all()

    return schemas.EvaluationResultPaginationResponse(
        items=results,
        total=total_count,
        page=current_page,
        size=size,
        pages=total_pages
    )