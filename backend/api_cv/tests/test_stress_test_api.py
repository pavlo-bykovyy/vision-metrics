"""Stress-test API layer: schemas, DB orchestration, result-file access (no Redis/Celery, no scipy)."""
from pathlib import Path

import pandas as pd
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shared import enums, models
from shared.database import Base
from api_cv.schemas import stress_tests as schemas
from api_cv.services import stress_test_service as service


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def dispatched(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(service, "_dispatch", lambda run_id: sent.append(run_id) or f"celery-{run_id}")
    monkeypatch.setattr(service, "_revoke", lambda _task_id: None)
    monkeypatch.setattr(service, "STRESS_TEST_ROOT", tmp_path)
    return sent


def test_schema_defaults_match_stress_test_config():
    np = pytest.importorskip("numpy")
    from api_cv.services.stress_test.config import (
        FAILURE_PATHS, NON_GAUSSIAN_DISTRIBUTIONS, PLATFORM_METRICS, StressTestConfig,
    )

    ref, ours = StressTestConfig(), schemas.StressTestConfigSchema()
    for field in ("seed", "n", "replicates", "mu", "sigma", "max_logit_bias", "min_temperature",
                  "max_temperature", "ood_replicates", "cv_splits", "n_boot",
                  "collapse_positive_target", "collapse_negative_target",
                  "severity_mild_max", "severity_moderate_max"):
        assert getattr(ours, field) == getattr(ref, field), field
    assert tuple(ours.prevalences) == ref.prevalences
    assert tuple(ours.ood_prevalences) == ref.ood_prevalences
    assert tuple(ours.ood_distributions) == ref.ood_distributions
    assert schemas.OOD_DISTRIBUTIONS == NON_GAUSSIAN_DISTRIBUTIONS
    assert tuple(ours.public_links) == ref.public_links
    assert ours.ood_crosscheck == ref.ood_crosscheck
    assert ours.severity_levels == len(ref.severities)
    np.testing.assert_allclose(np.round(np.linspace(0, 1, ours.severity_levels), 2), ref.severities)
    assert schemas.FAILURE_PATH_LABELS == [f"{a}:{b}" for a, b in FAILURE_PATHS]
    assert schemas.PLATFORM_METRICS == PLATFORM_METRICS


def test_steps_are_ordered_and_require_simulate():
    req = schemas.StressTestCreateRequest(steps=["figures", "simulate", "figures"])
    assert req.steps == ["simulate", "figures"]
    with pytest.raises(ValidationError):
        schemas.StressTestCreateRequest(steps=["reviewer"])


@pytest.mark.parametrize("bad", [
    {"prevalences": [0.0, 0.5]},
    {"prevalences": [0.3, 0.3]},
    {"replicates": 3, "cv_splits": 5},
    {"collapse_positive_target": 0.4},
    {"collapse_negative_target": 0.6},
    {"severity_mild_max": 0.7, "severity_moderate_max": 0.3},
    {"ood_distributions": ["Uniform"]},
    {"ood_distributions": []},
    {"public_links": ["x" * 501]},
    {"public_links": [f"Link {i}: https://example.org/{i}" for i in range(11)]},
])
def test_config_validation(bad):
    with pytest.raises(ValidationError):
        schemas.StressTestConfigSchema(**bad)


def test_create_cancel_rerun_delete(db, dispatched, tmp_path):
    req = schemas.StressTestCreateRequest(config={"replicates": 25}, figure_formats=["png", "svg"], figure_dpi=150)
    run = service.create_run(db, req)

    assert dispatched == [run.id]
    assert run.status == enums.TaskStatus.PENDING
    assert run.celery_task_id == f"celery-{run.id}"
    assert run.name == f"Stress test #{run.id}"
    assert Path(run.results_dir) == tmp_path / f"run_{run.id}"
    assert run.config["replicates"] == 25
    assert run.config["figure_formats"] == ["png", "svg"] and run.config["figure_dpi"] == 150

    with pytest.raises(HTTPException) as exc:
        service.delete_run(db, run.id)
    assert exc.value.status_code == 409

    service.cancel_run(db, run.id)
    assert run.status == enums.TaskStatus.CANCELLED
    with pytest.raises(HTTPException):
        service.cancel_run(db, run.id)

    clone = service.rerun(db, run.id)
    assert clone.id != run.id and clone.config == run.config and clone.steps == run.steps

    Path(run.results_dir).mkdir(parents=True)
    (Path(run.results_dir) / "metric_summary.csv").write_text("a\n1\n")
    service.delete_run(db, run.id)
    assert not Path(run.results_dir).exists()
    assert models.StressTestRun.get_by_id(db, run.id) is None


def test_dispatch_failure_marks_run_failed(db, monkeypatch, tmp_path):
    monkeypatch.setattr(service, "STRESS_TEST_ROOT", tmp_path)

    def boom(_run_id):
        raise ConnectionError("redis down")

    monkeypatch.setattr(service, "_dispatch", boom)
    with pytest.raises(HTTPException) as exc:
        service.create_run(db, schemas.StressTestCreateRequest())
    assert exc.value.status_code == 503
    run = db.query(models.StressTestRun).one()
    assert run.status == enums.TaskStatus.FAILED and "redis down" in run.error_message


def test_files_tables_and_traversal(db, dispatched):
    run = service.create_run(db, schemas.StressTestCreateRequest())
    root = Path(run.results_dir)
    (root / "publication_figures").mkdir(parents=True)
    (root / "publication_figures" / "Figure_01.png").write_bytes(b"\x89PNG")
    (root / "manuscript_ready_values.txt").write_text("values")
    pd.DataFrame({"x": [1.0, float("nan"), 3.0]}, index=["a", "b", "c"]).to_csv(root / "matrix.csv")
    pd.DataFrame({"y": range(10)}).to_csv(root / "raw.csv.gz", index=False, compression="gzip")

    files = {f.path: f.kind for f in service.list_files(run)}
    assert files == {
        "manuscript_ready_values.txt": "text",
        "matrix.csv": "table",
        "publication_figures/Figure_01.png": "figure",
        "raw.csv.gz": "table",
    }

    table = service.read_table(run, "matrix.csv", limit=500)
    assert table.columns == ["", "x"]
    assert table.rows == [["a", 1.0], ["b", None], ["c", 3.0]]

    gz = service.read_table(run, "raw.csv.gz", limit=4)
    assert gz.total_rows == 10 and gz.truncated and len(gz.rows) == 4
    exact = service.read_table(run, "raw.csv.gz", limit=10)
    assert exact.total_rows == 10 and not exact.truncated and len(exact.rows) == 10

    for bad in ("../run_999/x.csv", "/etc/passwd", "missing.csv"):
        with pytest.raises(HTTPException):
            service.resolve_file(run, bad)
    with pytest.raises(HTTPException):
        service.read_table(run, "manuscript_ready_values.txt", limit=10)


def test_worker_build_config():
    pytest.importorskip("numpy")
    from api_cv.services.stress_test_worker import build_config

    payload = {**schemas.StressTestConfigSchema(replicates=10, severity_levels=6).model_dump(),
               "figure_formats": ["svg"], "figure_dpi": 120}
    cfg, formats, dpi = build_config(payload)
    assert cfg.replicates == 10 and cfg.prevalences == (0.5, 0.3, 0.1, 0.05)
    assert list(cfg.severities) == [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    assert formats == ("svg",) and dpi == 120


def _worker(monkeypatch, db):
    pytest.importorskip("celery")
    from api_cv.services import stress_test_worker as worker

    class _Engine:
        def dispose(self):
            pass

    monkeypatch.setattr(worker, "engine", _Engine())
    monkeypatch.setattr(worker, "SessionLocal", lambda: db)
    return worker


def test_worker_skips_duplicate_delivery(db, dispatched, monkeypatch):
    worker = _worker(monkeypatch, db)
    run = service.create_run(db, schemas.StressTestCreateRequest())
    run.status = enums.TaskStatus.EVALUATING
    run.progress = 42.0
    db.commit()
    results = Path(run.results_dir)
    results.mkdir(parents=True)
    (results / "monte_carlo_raw_results.csv.gz").write_bytes(b"partial")

    worker.worker_stress_test.run(run.id)

    run = db.query(models.StressTestRun).one()
    assert run.status == enums.TaskStatus.EVALUATING and run.progress == 42.0
    assert (results / "monte_carlo_raw_results.csv.gz").exists()


def test_recover_retries_once_with_fewer_jobs_then_fails(db, dispatched, monkeypatch):
    worker = _worker(monkeypatch, db)
    first = service.create_run(db, schemas.StressTestCreateRequest(name="first attempt crashed"))
    second = service.create_run(db, schemas.StressTestCreateRequest(name="retry crashed too"))
    queued = service.create_run(db, schemas.StressTestCreateRequest(name="queued"))
    done = service.create_run(db, schemas.StressTestCreateRequest(name="done"))
    first.status, first.stage, first.progress = enums.TaskStatus.EVALUATING, "reviewer", 73.4
    second.status, second.stage, second.progress = enums.TaskStatus.EVALUATING, "reviewer", 71.0
    second.attempt, second.n_jobs = 2, 1
    done.status = enums.TaskStatus.COMPLETED
    db.commit()

    sent = []
    result = worker.recover_interrupted_runs(db, dispatch=lambda run_id: sent.append(run_id) or f"again-{run_id}")

    assert result == {"retried": 1, "failed": 1, "requeued": 2}
    for run in (first, second, queued, done):
        db.refresh(run)

    # first crash -> back to PENDING with n_jobs=1 and dispatched again
    assert first.status == enums.TaskStatus.PENDING and first.attempt == 2 and first.n_jobs == 1
    assert first.progress == 0.0 and first.stage is None and first.error_message is None
    assert first.celery_task_id == f"again-{first.id}"

    # second crash -> FAILED with a message for the user, not re-queued
    assert second.status == enums.TaskStatus.FAILED and second.finished_at is not None
    assert "'reviewer'" in second.error_message and "71.0%" in second.error_message
    assert "2/2" in second.error_message and "n_jobs=1" in second.error_message

    assert queued.status == enums.TaskStatus.PENDING and queued.celery_task_id == f"again-{queued.id}"
    assert done.status == enums.TaskStatus.COMPLETED
    assert sorted(sent) == sorted([first.id, queued.id])


def test_oom_error_detection():
    pytest.importorskip("celery")
    from api_cv.services.stress_test_worker import _is_oom_error

    class TerminatedWorkerError(Exception):
        pass

    wrapped = RuntimeError("probe failed")
    wrapped.__cause__ = TerminatedWorkerError("A worker process was killed (SIGKILL)")
    assert _is_oom_error(MemoryError())
    assert _is_oom_error(wrapped)
    assert not _is_oom_error(ValueError("bad config"))
