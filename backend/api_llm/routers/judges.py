from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from shared import schemas
from shared.database import get_db

from api_llm.services import judge_services


router = APIRouter(prefix="/judges", tags=["Judges Management"])


@router.post("/", response_model=schemas.JudgeResponse, status_code=status.HTTP_201_CREATED)
def create_judge(judge_in: schemas.JudgeBase, db: Session = Depends(get_db)):
    """
    Creates a new judge (LLM model) in the system.
    """
    return judge_services.create_judge(db=db, judge_in=judge_in)

@router.get("/", response_model=schemas.JudgePaginationResponse)
def get_judges(
        page: int = 1,
        size: int = 20,
        db: Session = Depends(get_db)
):
    """
    Returns a paginated list of all registered judges.
    """
    return judge_services.get_paginated_judges(db=db, page=page, size=size)

@router.get("/{judge_id}", response_model=schemas.JudgeResponse)
def get_judge(judge_id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed information about a specific judge by its ID.
    """
    return judge_services.get_judge(db=db, judge_id=judge_id)

@router.put("/{judge_id}", response_model=schemas.JudgeResponse)
def update_judge(judge_id: int, judge_in: schemas.JudgeBase, db: Session = Depends(get_db)):
    """
    Updates the name of an existing judge.
    """
    return judge_services.update_judge(db=db, judge_id=judge_id, judge_in=judge_in)

@router.delete("/{judge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_judge(judge_id: int, db: Session = Depends(get_db)):
    """
    Removes a judge from the database.
    """
    return judge_services.delete_judge(db=db, judge_id=judge_id)