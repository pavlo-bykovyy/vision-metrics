"""
VisionMetrics statistical stress test (paper experiment, ported from the Kaggle notebook).

Monte Carlo simulation of controlled classifier failure modes (collapse, score bias,
calibration drift, score inversion) evaluated with the platform's own binary metrics,
plus the diagnostic analyses and publication figures built on top of it.

Submodules import scipy/scikit-learn at top level, so this package belongs to the CV
worker image / research runs only; do not import it from routers or other API code.
Run it with `python -m api_cv.services.stress_test --help`.

    config      constants and StressTestConfig
    simulation  baselines, failure modes, platform-aligned metrics, Monte Carlo
    analysis    summaries, signatures, metric-family ablation, LOPO, manuscript tables
    reviewer    extended ablation + Wilcoxon, alternative probes, PCA, redundancy, OOD
    figures     publication figures (matplotlib, lazy)
    runner      writes all outputs to a results directory, archive
"""
from api_cv.services.stress_test.config import (
    ALL_DIAGNOSTIC_METRICS,
    FAILURE_PATHS,
    METRIC_FAMILIES,
    PATH_LABELS,
    PLATFORM_METRICS,
    PLATFORM_THRESHOLD,
    StressTestConfig,
)

__all__ = [
    "ALL_DIAGNOSTIC_METRICS",
    "FAILURE_PATHS",
    "METRIC_FAMILIES",
    "PATH_LABELS",
    "PLATFORM_METRICS",
    "PLATFORM_THRESHOLD",
    "StressTestConfig",
]
