import math
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from shared import models, schemas


def create_judge(db: Session, judge_in: schemas.JudgeBase) -> models.Judge:
    """
    Creates a new judge in the database.

    Uses IntegrityError to handle duplicate model_name entries efficiently.
    """
    new_judge = models.Judge(
        model_name=judge_in.model_name,
        name=judge_in.name,
        description=judge_in.description
    )
    db.add(new_judge)

    try:
        db.commit()
        db.refresh(new_judge)
        return new_judge
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Judge with model_name '{judge_in.model_name}' already exists."
        )


def get_paginated_judges(db: Session, page: int, size: int) -> Dict[str, Any]:
    """
    Retrieves a paginated list of registered judges from the database.
    """
    query = db.query(models.Judge)

    total_count = query.count()
    total_pages = math.ceil(total_count / size) if total_count > 0 else 0

    current_page = max(1, page)
    skip = (current_page - 1) * size

    results = query.order_by(models.Judge.id.desc()).offset(skip).limit(size).all()

    return {
        "items": results,
        "total": total_count,
        "page": current_page,
        "size": size,
        "pages": total_pages
    }

def get_judge(db: Session, judge_id: int) -> models.Judge:
    """
    Retrieves a specific judge by their unique ID.

    Raises:
        HTTPException: If the judge is not found (404 Not Found).
    """
    judge = db.query(models.Judge).filter(models.Judge.id == judge_id).first()
    if not judge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Judge not found."
        )
    return judge

def update_judge(db: Session, judge_id: int, judge_in: schemas.JudgeBase) -> models.Judge:
    """
    Updates the model name of an existing judge.

    Raises:
        HTTPException: If the judge is not found (404 Not Found).
        HTTPException: If the new model_name is already taken by another judge (400 Bad Request).
    """
    judge = get_judge(db, judge_id)

    existing_judge = db.query(models.Judge).filter(models.Judge.model_name == judge_in.model_name).first()
    if existing_judge and existing_judge.id != judge_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another judge with this model_name already exists."
        )

    judge.model_name = judge_in.model_name
    db.commit()
    db.refresh(judge)

    return judge

def delete_judge(db: Session, judge_id: int) -> None:
    """
    Deletes a judge from the database by their ID.

    Raises:
        HTTPException: If the judge is not found (404 Not Found).
    """
    judge = get_judge(db, judge_id)

    db.delete(judge)
    db.commit()