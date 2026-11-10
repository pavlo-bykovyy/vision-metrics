"""File-writing orchestration of the stress test (simulation -> reviewer analyses -> figures -> archive)."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

from shared.utils.logger import get_logger
from api_cv.services.stress_test.config import FAILURE_PATHS, StressTestConfig

logger = get_logger(__name__)

RAW_RESULTS_FILE = "monte_carlo_raw_results.csv.gz"


def _write(results_dir: Path, outputs: dict[str, Any]) -> list[Path]:
    """Writes DataFrames (index kept only when it carries labels) and text outputs."""
    results_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for name, obj in outputs.items():
        path = results_dir / name
        if isinstance(obj, pd.DataFrame):
            keep_index = not isinstance(obj.index, pd.RangeIndex)
            obj.to_csv(path, index=keep_index, compression="gzip" if name.endswith(".gz") else None)
        else:
            path.write_text(str(obj), encoding="utf-8")
        saved.append(path)
    return saved


def load_raw_results(results_dir: Path) -> pd.DataFrame:
    path = Path(results_dir) / RAW_RESULTS_FILE
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: run the 'simulate' step first.")
    return pd.read_csv(path)


def run_simulation(
    cfg: StressTestConfig,
    results_dir: Path,
    progress: Optional[Callable[[int, int], None]] = None,
) -> pd.DataFrame:
    """
    Stress test v4: Monte Carlo + summaries, signatures, ablation, LOPO, invariance, manuscript tables.

    `progress(done, total)` is called from the Monte Carlo loop in addition to logging; it may raise
    to abort the run (the Celery task uses this for cancellation).
    """
    # scipy/sklearn are imported per step so `figures`/`archive` work without them.
    from api_cv.services.stress_test import analysis
    from api_cv.services.stress_test.simulation import run_monte_carlo

    results_dir = Path(results_dir)
    logger.info(
        "Stress test: N=%s, R=%s, prevalences=%s, paths=%s",
        cfg.n, cfg.replicates, list(cfg.prevalences), [f"{a}:{b}" for a, b in FAILURE_PATHS],
    )

    def _progress(done: int, total: int) -> None:
        logger.info("Monte Carlo progress: %s/%s", done, total)
        if progress is not None:
            progress(done, total)

    raw = run_monte_carlo(cfg, progress=_progress)
    _write(results_dir, {RAW_RESULTS_FILE: raw})

    summary = analysis.summarize_results(raw)
    sig_prev, sig_agg = analysis.build_signature_matrix(summary)
    logger.info("Metric-family ablation (%s-fold GroupKFold)", cfg.cv_splits)
    ablation = analysis.run_metric_family_ablation(
        raw, n_splits=cfg.cv_splits, band_edges=cfg.severity_band_edges
    )
    invariance = analysis.theoretical_invariance_checks(summary)
    logger.info("Leave-one-prevalence-out validation")
    loo_perf, loo_pred = analysis.leave_one_prevalence_out_validation(
        raw, list(cfg.prevalences), band_edges=cfg.severity_band_edges
    )

    outputs: dict[str, Any] = {
        "metric_summary.csv": summary,
        "metric_sensitivity.csv": analysis.sensitivity_table(summary),
        "failure_signatures_by_prevalence.csv": sig_prev,
        "failure_signature_matrix.csv": sig_agg,
        "metric_family_ablation.csv": ablation["performance"],
        "metric_family_cv_folds.csv": ablation["folds"],
        "failure_mode_confusion_matrix.csv": ablation["confusion_matrix"],
        "failure_mode_classification_report.csv": ablation["classification_report"],
        "invariance_checks.csv": invariance,
        "leave_one_prevalence_out.csv": loo_perf,
        "leave_one_prevalence_out_predictions.csv.gz": loo_pred,
        "simulation_design.csv": analysis.simulation_design_table(cfg),
        **analysis.build_publication_tables(
            raw=raw,
            fold_performance=ablation["folds"],
            family_performance=ablation["performance"],
            loo_performance=loo_perf,
            invariance=invariance,
        ),
    }
    _write(results_dir, outputs)
    logger.info("Simulation outputs written to %s", results_dir.resolve())
    return raw


def run_reviewer(
    cfg: StressTestConfig,
    results_dir: Path,
    raw: Optional[pd.DataFrame] = None,
    n_jobs: int = -1,
    log: Optional[Callable[[str], None]] = None,
) -> list[Path]:
    from api_cv.services.stress_test.reviewer import run_reviewer_analyses

    results_dir = Path(results_dir)
    raw = raw if raw is not None else load_raw_results(results_dir)

    def _log(msg: str) -> None:
        logger.info(msg)
        if log is not None:
            log(msg)

    outputs = run_reviewer_analyses(raw, cfg, n_jobs=n_jobs, progress=_log)
    saved = _write(results_dir, outputs)
    logger.info("Reviewer outputs written to %s", results_dir.resolve())
    return saved


def run_figures(results_dir: Path, formats: tuple[str, ...] = ("png", "pdf", "svg"), dpi: int = 600) -> list[Path]:
    from api_cv.services.stress_test.figures import generate_publication_figures

    saved = generate_publication_figures(Path(results_dir), formats=formats, dpi=dpi, log=logger.info)
    logger.info("%s figure files written", len(saved))
    return saved


def archive_results(results_dir: Path, archive_base: Optional[Path] = None) -> Path:
    """Zips the whole results directory next to it and verifies the archive."""
    results_dir = Path(results_dir).resolve()
    files = [f for f in results_dir.rglob("*") if f.is_file()]
    if not files:
        raise RuntimeError(f"The folder {results_dir} is empty.")

    base = archive_base or results_dir.parent / "VisionMetrics_Stress_Test_v3_Complete_Results"
    archive = Path(shutil.make_archive(str(base), "zip", root_dir=results_dir.parent, base_dir=results_dir.name))

    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
    if bad is not None:
        raise RuntimeError(f"Corrupted file in archive: {bad}")

    total = sum(f.stat().st_size for f in files)
    logger.info(
        "Archive %s: %s files, %.2f MB (ratio %.3f)",
        archive, len(files), archive.stat().st_size / 1024**2, archive.stat().st_size / max(total, 1),
    )
    return archive
