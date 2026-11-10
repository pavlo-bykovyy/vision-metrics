from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api_cv.schemas import stress_tests as schemas
from api_cv.services import stress_test_service as service
from shared import models
from shared.database import get_db
from shared.dependencies import verify_token
from shared.utils.logger import get_logger


logger = get_logger("STRESS-TEST-ROUTER")

router = APIRouter(prefix="/stress-tests", tags=["Stress Tests"])


@router.get("/defaults", response_model=schemas.StressTestDefaults)
def get_defaults(current_user: dict = Depends(verify_token)):
    """
    Default simulation design (the article run), available pipeline steps, the failure paths
    and the platform metrics the stress test evaluates.
    """
    return service.defaults()


@router.get("/", response_model=schemas.StressTestPaginationResponse)
def list_runs(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(verify_token)
):
    """Paginated list of stress-test runs, newest first."""
    items, total, pages = models.StressTestRun.get_paginated(db, page, size)
    return schemas.StressTestPaginationResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=schemas.StressTestRun, status_code=201)
def create_run(
        request: schemas.StressTestCreateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Create a stress-test run and queue it on the CV worker (`cv.stress_test`, queue `cv_tasks`).

    Steps always start with `simulate`; `reviewer`, `figures` and `archive` are optional.
    """
    return service.create_run(db, request)


@router.get("/{run_id}", response_model=schemas.StressTestRun)
def get_run(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """Run status, current stage, progress (0-100) and configuration."""
    return service.get_run_or_404(db, run_id)


@router.delete("/{run_id}")
def delete_run(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """Delete a finished run together with its results directory and archive."""
    service.delete_run(db, run_id)
    return {"message": f"Stress test run {run_id} successfully deleted"}


@router.post("/{run_id}/cancel", response_model=schemas.StressTestRun)
def cancel_run(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """Cancel a pending or running stress test."""
    return service.cancel_run(db, run_id)


@router.post("/{run_id}/re-run", response_model=schemas.StressTestRun, status_code=201)
def rerun(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """Start a new run with the same configuration and steps."""
    return service.rerun(db, run_id)


@router.get("/{run_id}/files", response_model=list[schemas.StressTestFile])
def list_files(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """All files written by the run (tables, figures, text), relative to its results directory."""
    return service.list_files(service.get_run_or_404(db, run_id))


@router.get("/{run_id}/tables", response_model=schemas.StressTestTable)
def read_table(
        run_id: int,
        name: str = Query(..., description="Relative path of a .csv / .csv.gz file from /files"),
        limit: int = Query(500, ge=1, le=5000),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """Parsed table preview (first `limit` rows) for rendering in the UI."""
    return service.read_table(service.get_run_or_404(db, run_id), name, limit)


@router.get("/{run_id}/files/{file_path:path}")
def download_file(
        run_id: int,
        file_path: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """Raw file (figure, table or text) from the run's results directory."""
    path = service.resolve_file(service.get_run_or_404(db, run_id), file_path)
    return FileResponse(path, filename=path.name)


@router.get("/{run_id}/archive")
def download_archive(run_id: int, db: Session = Depends(get_db), current_user: dict = Depends(verify_token)):
    """ZIP archive of all outputs (only when the run included the `archive` step)."""
    path = service.get_archive(service.get_run_or_404(db, run_id))
    return FileResponse(path, filename=path.name, media_type="application/zip")
