from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from shared import schemas
from shared.database import get_db
from api_llm.judge import judge_task_runs_services


router = APIRouter(prefix="/judge-runs", tags=["Judge Task Runs Management"])


@router.get("/evaluation-tasks/", response_model=schemas.EvaluationTaskListResponse)
def get_evaluation_tasks_for_judge(
        size: int = 100,
        db: Session = Depends(get_db)
):
    """
    Retrieves evaluation tasks to populate the dropdown in the Judge UI.
    Delegates the data fetching logic to the service layer.
    """
    return judge_task_runs_services.get_evaluation_tasks_for_judge_ui(db=db, size=size)

@router.post("/", response_model=schemas.JudgeTaskRunResponse, status_code=status.HTTP_201_CREATED)
def create_judge_run_endpoint(
        payload: schemas.JudgeRunCreate,
        db: Session = Depends(get_db)
):
    """
    Creates a new automated judge task run.
    Accepts evaluation_task_id, judge_id, and configurations.
    """
    try:
        return judge_task_runs_services.create_judge_run(db=db, payload=payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=schemas.JudgeTaskRunPaginationResponse)
def get_judge_runs(
        page: int = 1,
        size: int = 20,
        db: Session = Depends(get_db)
):
    """
    Returns a paginated list of all automated judge tasks.
    """
    return judge_task_runs_services.get_paginated_judge_runs(db=db, page=page, size=size)

@router.post("/{run_id}/cancel", response_model=schemas.JudgeTaskRunResponse)
def cancel_judge_run_endpoint(run_id: int, db: Session = Depends(get_db)):
    try:
        return judge_task_runs_services.cancel_judge_run(db=db, run_id=run_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_judge_run_endpoint(run_id: int, db: Session = Depends(get_db)):
    try:
        judge_task_runs_services.delete_judge_run(db=db, run_id=run_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))