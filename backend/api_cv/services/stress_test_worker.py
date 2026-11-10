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
                cfg, results_dir, raw=raw, n_jobs=-1,
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
            run.status = enums.TaskStatus.FAILED
            run.error_message = str(e)[:2000]
            run.finished_at = datetime.now(timezone.utc)
            db.commit()

    finally:
        db.close()
