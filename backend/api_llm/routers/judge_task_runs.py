from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from shared import schemas
from shared.database import get_db
from api_llm.judge import judge_task_runs_services


router = APIRouter(prefix="/judge-runs", tags=["Judge Task Runs Management"])


@router.get("/judge-runs/", response_model=schemas.TaskListResponse)
def get_judge_runs(
        size: int = 100,
        db: Session = Depends(get_db)
):
    """
    Retrieves judge runs for the Judge Tasks table.

    Replaces the previous ``GET /judge-runs/`` handler. Delegates the data
    fetching and mapping logic to the service layer.
    """
    return judge_task_runs_services.list_judge_runs(db=db, size=size)


@router.get("/evaluation-tasks/list", response_model=schemas.TaskListResponse)
def get_evaluation_tasks(
        size: int = 100,
        db: Session = Depends(get_db)
):
    """
    Retrieves evaluation tasks for a tasks table using the universal list shape.

    Unlike ``GET /evaluation-tasks/``, which feeds the Judge dropdown with full
    task details, this endpoint returns flat rows ready for ``TasksTable``.
    """
    return judge_task_runs_services.list_evaluation_tasks(db=db, size=size)

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

@router.get("/{run_id}", response_model=schemas.JudgeTaskRunResponse)
def get_judge_run_endpoint(run_id: int, db: Session = Depends(get_db)):
    """
    Returns details of a single judge task run.
    """
    return judge_task_runs_services.get_judge_run(db=db, run_id=run_id)

@router.get("/{run_id}/results", response_model=schemas.JudgeRunResultsPaginationResponse)
def get_judge_run_results_endpoint(
        run_id: int,
        page: int = 1,
        size: int = 50,
        db: Session = Depends(get_db)
):
    """
    Returns paginated judge verdicts (scores + reasoning) for a judge task run,
    together with the evaluated input/generated text.
    """
    return judge_task_runs_services.get_judge_run_results(db=db, run_id=run_id, page=page, size=size)

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