"""
stress_test_service.py

DB orchestration and Celery dispatch of statistical stress-test runs, plus read access to the
files a run writes (tables, figures, archive).

Runs on the API side: it must not import `api_cv.services.stress_test` (scipy/scikit-learn live
only in the CV worker image). The heavy work happens in `api_cv.services.stress_test_worker`.
"""
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from shared import enums, models
from shared.config import UPLOAD_DIR
from shared.utils.logger import get_logger
from api_cv.schemas import stress_tests as schemas


logger = get_logger(__name__)

STRESS_TEST_TASK = "cv.stress_test"
STRESS_TEST_QUEUE = "cv_tasks"

# Shared between the `api` and `celery_worker_cv` containers (uploaded_models volume).
STRESS_TEST_ROOT = Path(UPLOAD_DIR) / "stress_tests"

ACTIVE_STATUSES = (enums.TaskStatus.PENDING, enums.TaskStatus.EVALUATING)

TABLE_SUFFIXES = (".csv", ".csv.gz")
FIGURE_SUFFIXES = (".png", ".svg", ".pdf")
TEXT_SUFFIXES = (".txt", ".md")


# ---------------------------------------------------------------------------
# Run lifecycle
# ---------------------------------------------------------------------------

def get_run_or_404(db: Session, run_id: int) -> models.StressTestRun:
    run = models.StressTestRun.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Stress test run not found")
    return run


def _dispatch(run_id: int) -> str:
    from api_cv.services.celery_app import celery_app

    async_result = celery_app.send_task(
        name=STRESS_TEST_TASK,
        queue=STRESS_TEST_QUEUE,
        kwargs={"run_id": run_id},
    )
    logger.info(f"Dispatched stress test run_id={run_id} to Celery. Task ID: {async_result.id}")
    return async_result.id


def _create_and_dispatch(db: Session, name: Optional[str], config: dict, steps: list[str]) -> models.StressTestRun:
    run = models.StressTestRun(
        name=name,
        status=enums.TaskStatus.PENDING,
        config=config,
        steps=steps,
        progress=0.0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    run.results_dir = str(STRESS_TEST_ROOT / f"run_{run.id}")
    if not run.name:
        run.name = f"Stress test #{run.id}"

    try:
        run.celery_task_id = _dispatch(run.id)
    except Exception as e:
        logger.warning(f"Failed to dispatch stress test run_id={run.id}: {e}", exc_info=True)
        run.status = enums.TaskStatus.FAILED
        run.error_message = f"Queue dispatch error: {e}"
        db.commit()
        raise HTTPException(status_code=503, detail="Could not queue the stress test (Celery/Redis unavailable)")

    db.commit()
    db.refresh(run)
    return run


def create_run(db: Session, request: schemas.StressTestCreateRequest) -> models.StressTestRun:
    """Stores the run (config + figure options in one JSON) and queues `cv.stress_test`."""
    config = {
        **request.config.model_dump(),
        "figure_formats": list(request.figure_formats),
        "figure_dpi": request.figure_dpi,
    }
    return _create_and_dispatch(db, request.name, config, list(request.steps))


def rerun(db: Session, run_id: int) -> models.StressTestRun:
    """Starts a new run with the same configuration; the old run and its files are kept."""
    old = get_run_or_404(db, run_id)
    return _create_and_dispatch(db, f"{old.name or f'Stress test #{old.id}'} (re-run)", dict(old.config), list(old.steps))


def cancel_run(db: Session, run_id: int) -> models.StressTestRun:
    """
    Marks the run CANCELLED. A queued task is revoked; a running one notices the status at its
    next progress checkpoint and stops.
    """
    run = get_run_or_404(db, run_id)
    if run.status not in ACTIVE_STATUSES:
        raise HTTPException(status_code=400, detail=f"Cannot cancel run with status '{run.status.value}'")

    run.status = enums.TaskStatus.CANCELLED
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)

    if run.celery_task_id:
        _revoke(run.celery_task_id)

    logger.info(f"Stress test run {run_id} cancelled")
    return run


def _revoke(celery_task_id: str) -> None:
    try:
        from api_cv.services.celery_app import celery_app
        celery_app.control.revoke(celery_task_id)
    except Exception as e:  # the worker-side status check still stops a running task
        logger.warning(f"Could not revoke Celery task {celery_task_id}: {e}")


def delete_run(db: Session, run_id: int) -> None:
    run = get_run_or_404(db, run_id)
    if run.status in ACTIVE_STATUSES:
        raise HTTPException(status_code=409, detail="Cancel the run before deleting it")

    for target in (run.results_dir, run.archive_path):
        if not target:
            continue
        path = Path(target)
        if not _is_within(path, STRESS_TEST_ROOT):
            logger.warning(f"Refusing to delete {path}: outside {STRESS_TEST_ROOT}")
            continue
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()

    db.delete(run)
    db.commit()


# ---------------------------------------------------------------------------
# Result files
# ---------------------------------------------------------------------------

def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _file_kind(name: str) -> str:
    lower = name.lower()
    if lower.endswith(TABLE_SUFFIXES):
        return "table"
    if lower.endswith(FIGURE_SUFFIXES):
        return "figure"
    if lower.endswith(TEXT_SUFFIXES):
        return "text"
    return "other"


def _results_dir(run: models.StressTestRun) -> Path:
    if not run.results_dir:
        raise HTTPException(status_code=404, detail="Run has no results directory")
    return Path(run.results_dir)


def list_files(run: models.StressTestRun) -> list[schemas.StressTestFile]:
    root = _results_dir(run)
    if not root.is_dir():
        return []
    files = [
        schemas.StressTestFile(
            path=f.relative_to(root).as_posix(),
            kind=_file_kind(f.name),
            size_bytes=f.stat().st_size,
        )
        for f in root.rglob("*")
        if f.is_file()
    ]
    return sorted(files, key=lambda f: f.path)


def resolve_file(run: models.StressTestRun, relative_path: str) -> Path:
    """Maps a client-supplied relative path to a file inside the run's directory (no traversal)."""
    root = _results_dir(run)
    path = root / relative_path
    if not _is_within(path, root) or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return path


def _json_cell(value):
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, "item"):  # numpy scalar
        return _json_cell(value.item())
    return value


def read_table(run: models.StressTestRun, name: str, limit: int) -> schemas.StressTestTable:
    path = resolve_file(run, name)
    if _file_kind(path.name) != "table":
        raise HTTPException(status_code=400, detail="Not a table file")

    df = pd.read_csv(path)
    df.columns = ["" if str(c).startswith("Unnamed:") else str(c) for c in df.columns]
    total = len(df)
    head = df.head(limit).astype(object)
    rows = [[_json_cell(v) for v in row] for row in head.itertuples(index=False, name=None)]

    return schemas.StressTestTable(
        name=name,
        columns=list(df.columns),
        rows=rows,
        total_rows=total,
        truncated=total > limit,
    )


def get_archive(run: models.StressTestRun) -> Path:
    if not run.archive_path or not Path(run.archive_path).is_file():
        raise HTTPException(status_code=404, detail="Archive not available for this run")
    return Path(run.archive_path)


def defaults() -> schemas.StressTestDefaults:
    base = schemas.StressTestCreateRequest()
    return schemas.StressTestDefaults(
        config=base.config,
        steps=list(schemas.STEP_ORDER),
        figure_formats=list(base.figure_formats),
        figure_dpi=base.figure_dpi,
        failure_paths=schemas.FAILURE_PATH_LABELS,
        platform_metrics=schemas.PLATFORM_METRICS,
        ood_distributions=schemas.OOD_DISTRIBUTIONS,
    )
