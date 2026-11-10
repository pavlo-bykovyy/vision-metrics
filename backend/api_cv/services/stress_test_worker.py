"""
stress_test_worker.py

Celery task `cv.stress_test`: runs the requested stress-test steps for one `StressTestRun`
(simulate -> reviewer -> figures -> archive), reporting stage/progress to the DB and stopping
when the run is cancelled.

scipy/scikit-learn/matplotlib are imported lazily inside the task (CV worker image only).
"""
import shutil
from datetime import datetime, timezone
from pathlib import Path

from celery.signals import worker_ready

from shared import enums, models
from shared.database import SessionLocal, engine
from shared.utils.logger import get_logger
from api_cv.services.celery_app import celery_app


logger = get_logger(__name__)

# Relative share of the total progress bar per step (normalised over the requested steps).
STEP_WEIGHTS = {"simulate": 70.0, "reviewer": 20.0, "figures": 8.0, "archive": 2.0}


class StressTestCancelled(Exception):
    pass


def build_config(config: dict):
    """Run JSON config -> (StressTestConfig, figure formats, figure dpi)."""
    import numpy as np
    from api_cv.services.stress_test.config import StressTestConfig

    cfg = dict(config)
    formats = tuple(cfg.pop("figure_formats", None) or ("png",))
    dpi = int(cfg.pop("figure_dpi", 300))
    levels = int(cfg.pop("severity_levels", 11))
    for key in ("prevalences", "ood_prevalences"):
        if key in cfg:
            cfg[key] = tuple(float(v) for v in cfg[key])
    for key in ("ood_distributions", "public_links"):
        if key in cfg:
            cfg[key] = tuple(cfg[key])
    cfg["severities"] = np.round(np.linspace(0.0, 1.0, levels), 2)
    return StressTestConfig(**cfg), formats, dpi


class _Progress:
    """Writes stage/progress to the run row and raises StressTestCancelled once the API cancels it."""

    def __init__(self, db, run: models.StressTestRun):
        self.db = db
        self.run = run
        steps = [s for s in run.steps if s in STEP_WEIGHTS]
        total = sum(STEP_WEIGHTS[s] for s in steps) or 1.0
        self.offsets, acc = {}, 0.0
        for s in steps:
            self.offsets[s] = (acc / total * 100.0, STEP_WEIGHTS[s] / total * 100.0)
            acc += STEP_WEIGHTS[s]

    def check_cancelled(self) -> None:
        self.db.refresh(self.run, attribute_names=["status"])
        if self.run.status == enums.TaskStatus.CANCELLED:
            raise StressTestCancelled()

    def update(self, stage: str, fraction: float = 0.0) -> None:
        self.check_cancelled()
        start, width = self.offsets.get(stage, (self.run.progress or 0.0, 0.0))
        self.run.stage = stage
        self.run.progress = round(min(100.0, start + width * max(0.0, min(1.0, fraction))), 1)
        self.db.commit()


@celery_app.task(bind=True, name="cv.stress_test", queue="cv_tasks")
def worker_stress_test(self, run_id: int):
    logger.info(f"Stress test worker started for run_id: {run_id}")
    engine.dispose()
    db = SessionLocal()
    try:
        # Atomic claim: only a PENDING run may start. A duplicate delivery of the same message
        # (broker redelivery, worker restart, manual re-queue) must not wipe results_dir and
        # restart the Monte Carlo of a run that is already running or finished.
        claimed = (
            db.query(models.StressTestRun)
            .filter(
                models.StressTestRun.id == run_id,
                models.StressTestRun.status == enums.TaskStatus.PENDING,
            )
            .update(
                {
                    models.StressTestRun.status: enums.TaskStatus.EVALUATING,
                    models.StressTestRun.started_at: datetime.now(timezone.utc),
                    models.StressTestRun.progress: 0.0,
                    models.StressTestRun.error_message: None,
                },
                synchronize_session=False,
            )
        )
        db.commit()

        run = db.query(models.StressTestRun).filter(models.StressTestRun.id == run_id).first()
        if not run:
            logger.warning(f"Stress test run {run_id} not found")
            return
        if not claimed:
            logger.warning(
                f"Stress test run {run_id} skipped: status is '{run.status.value}', not 'pending' "
                f"(duplicate delivery or cancelled before start)"
            )
            return

        from api_cv.services.stress_test import runner

        cfg, formats, dpi = build_config(run.config or {})
        results_dir = Path(run.results_dir)
        if results_dir.exists():
            shutil.rmtree(results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)

        progress = _Progress(db, run)
        steps = list(run.steps or [])
        raw = None

        if "simulate" in steps:
            progress.update("simulate")
            # Monte Carlo is ~80% of the simulate step; the analyses after it are the rest.
            raw = runner.run_simulation(
                cfg, results_dir, progress=lambda done, total: progress.update("simulate", 0.8 * done / total)
            )

        if "reviewer" in steps:
            progress.update("reviewer")
            # one log message per block: dataset, A, B, C, D, E (+ OOD cross-check)
            n_blocks = 7 if cfg.ood_crosscheck else 6
            blocks = iter(range(1, n_blocks + 1))
            runner.run_reviewer(
                cfg, results_dir, raw=raw, n_jobs=run.n_jobs if run.n_jobs is not None else DEFAULT_N_JOBS,
                log=lambda _msg: progress.update("reviewer", next(blocks, n_blocks) / n_blocks),
            )
        del raw

        if "figures" in steps:
            progress.update("figures")
            runner.run_figures(results_dir, formats=formats, dpi=dpi)

        if "archive" in steps:
            progress.update("archive")
            archive = runner.archive_results(results_dir, archive_base=results_dir.parent / f"run_{run_id}_results")
            run.archive_path = str(archive)

        progress.check_cancelled()
        run.status = enums.TaskStatus.COMPLETED
        run.stage = None
        run.progress = 100.0
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Stress test run {run_id} completed")

    except StressTestCancelled:
        db.rollback()
        logger.info(f"Stress test run {run_id} stopped: cancelled by user")

    except Exception as e:
        logger.warning(f"Stress test run {run_id} failed: {e}", exc_info=True)
        db.rollback()
        run = db.query(models.StressTestRun).filter(models.StressTestRun.id == run_id).first()
        if run and run.status != enums.TaskStatus.CANCELLED:
            if _is_oom_error(e):
                # A joblib child was OOM-killed (or MemoryError): same policy as a worker crash.
                if _retry_or_fail(run, f"ran out of memory ({type(e).__name__})"):
                    db.commit()
                    try:
                        run.celery_task_id = _dispatch(run.id)
                    except Exception as dispatch_err:
                        # Stays PENDING; recover_interrupted_runs re-queues it on the next worker start.
                        logger.warning(f"Could not re-queue stress test run {run_id}: {dispatch_err}")
                db.commit()
            else:
                # Ordinary exceptions are deterministic: retrying would fail the same way.
                run.status = enums.TaskStatus.FAILED
                run.error_message = str(e)[:2000]
                run.finished_at = datetime.now(timezone.utc)
                db.commit()

    finally:
        db.close()


# ---------------------------------------------------------------------------
# Crash handling: one automatic retry with reduced parallelism, then FAILED
# ---------------------------------------------------------------------------

# Attempt 1 uses all cores (n_jobs=-1 in the reviewer step); attempt 2 runs single-process.
MAX_ATTEMPTS = 2
RETRY_N_JOBS = 1
DEFAULT_N_JOBS = -1

# Raised in the parent process when the kernel OOM-kills a joblib/loky child (the parent survives).
_OOM_ERROR_NAMES = {"MemoryError", "TerminatedWorkerError", "BrokenProcessPool"}


def _is_oom_error(exc: BaseException) -> bool:
    return any(type(e).__name__ in _OOM_ERROR_NAMES for e in (exc, exc.__cause__, exc.__context__) if e)


def _dispatch(run_id: int) -> str:
    return worker_stress_test.apply_async(kwargs={"run_id": run_id}, queue="cv_tasks").id


def _where(run: models.StressTestRun) -> str:
    return f"stage '{run.stage or 'unknown'}' at {run.progress or 0:.1f}%"


def _retry_or_fail(run: models.StressTestRun, reason: str) -> bool:
    """
    Puts a crashed run back to PENDING with n_jobs=1 if it still has an attempt left (True),
    otherwise marks it FAILED with a message for the user (False). The caller commits and,
    on True, dispatches the run.
    """
    attempt = run.attempt or 1
    if attempt < MAX_ATTEMPTS:
        logger.warning(
            f"Stress test run {run.id}: attempt {attempt}/{MAX_ATTEMPTS} {reason} during {_where(run)}; "
            f"retrying with n_jobs={RETRY_N_JOBS}"
        )
        run.attempt = attempt + 1
        run.n_jobs = RETRY_N_JOBS
        run.status = enums.TaskStatus.PENDING
        run.stage = None
        run.progress = 0.0
        run.started_at = None
        run.finished_at = None
        run.error_message = None
        return True

    n_jobs = run.n_jobs if run.n_jobs is not None else DEFAULT_N_JOBS
    run.status = enums.TaskStatus.FAILED
    run.finished_at = datetime.now(timezone.utc)
    run.error_message = (
        f"The CV worker {reason} during {_where(run)} on attempt {attempt}/{MAX_ATTEMPTS} "
        f"(n_jobs={n_jobs}); the automatic retry with reduced parallelism did not help. "
        f"Most likely out of memory: lower R / N or the number of prevalences, or give the "
        f"celery_worker_cv container more RAM, then use Re-run."
        if attempt > 1 else
        f"The CV worker {reason} during {_where(run)} (n_jobs={n_jobs}). Use Re-run to start again."
    )
    logger.warning(f"Stress test run {run.id} marked FAILED: {run.error_message}")
    return False


def recover_interrupted_runs(db, dispatch=None) -> dict[str, int]:
    """
    Repairs runs left behind by a worker that died mid-run (OOM kill, container restart, host
    reboot). Called when the CV worker starts, before it consumes any task.

    - EVALUATING: the worker runs with --pool=solo and is the only consumer of `cv.stress_test`,
      so nothing can still be executing these runs. A run on its first attempt is retried once
      with n_jobs=1; a run that already used its retry becomes FAILED with a message.
    - PENDING: dispatched again, its message may have been lost (e.g. `redis-cli flushall`). If the
      original message is still queued, the extra delivery is skipped by the atomic PENDING claim
      in `worker_stress_test`, so re-dispatching is always safe.

    Assumes a single CV worker container; with several replicas a starting worker would treat
    runs of its siblings as interrupted.
    """
    dispatch = dispatch or _dispatch

    interrupted = (
        db.query(models.StressTestRun)
        .filter(models.StressTestRun.status == enums.TaskStatus.EVALUATING)
        .all()
    )
    retried = sum(_retry_or_fail(run, "stopped (container restart or out-of-memory kill)") for run in interrupted)
    db.commit()

    pending = (
        db.query(models.StressTestRun)
        .filter(models.StressTestRun.status == enums.TaskStatus.PENDING)
        .order_by(models.StressTestRun.id)
        .all()
    )
    requeued = 0
    for run in pending:
        try:
            run.celery_task_id = dispatch(run.id)
            requeued += 1
        except Exception as e:
            logger.warning(f"Could not re-queue stress test run {run.id}: {e}")
    db.commit()

    return {"retried": retried, "failed": len(interrupted) - retried, "requeued": requeued}


@worker_ready.connect
def _recover_on_worker_start(sender=None, **_kwargs):
    # This module is loaded only by the CV worker (api_cv.services.celery_app include=).
    engine.dispose()
    db = SessionLocal()
    try:
        result = recover_interrupted_runs(db)
        logger.info(
            f"Stress test crash recovery: {result['retried']} retried, {result['failed']} failed, "
            f"{result['requeued']} queued"
        )
    except Exception as e:
        db.rollback()
        logger.warning(f"Stress test crash recovery failed: {e}", exc_info=True)
    finally:
        db.close()
