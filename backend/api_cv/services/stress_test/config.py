"""Constants and run configuration of the VisionMetrics statistical stress test."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

DEFAULT_SEED = 20260822

# EXACT deployed VisionMetrics binary rule (metrics_calculator.py): y_pred = probs > 0.5
PLATFORM_THRESHOLD = 0.5

EPS = float(np.finfo(float).eps)

FAILURE_PATHS: list[tuple[str, str]] = [
    ("collapse", "positive"),
    ("collapse", "negative"),
    ("score_bias", "positive"),
    ("score_bias", "negative"),
    ("calibration_drift", "over"),
    ("calibration_drift", "under"),
    ("score_inversion", "none"),
]
PATH_LABELS: list[str] = [f"{mode}:{direction}" for mode, direction in FAILURE_PATHS]

# Names mirror the platform `Metric` columns.
PLATFORM_METRICS: list[str] = [
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "mcc",
    "balanced_accuracy",
    "roc_auc",
    "pr_auc",
    "log_loss_value",
    "brier_score",
]

# Specificity is not a native metrics_calculator output; it is derived from TN/FP.
ALL_DIAGNOSTIC_METRICS: list[str] = PLATFORM_METRICS + ["specificity_derived"]

METRIC_FAMILIES: dict[str, list[str]] = {
    "full_panel": ALL_DIAGNOSTIC_METRICS,
    "threshold_confusion": [
        "accuracy", "precision", "recall", "f1_score",
        "mcc", "balanced_accuracy", "specificity_derived",
    ],
    "ranking_only": ["roc_auc", "pr_auc"],
    "probability_only": ["log_loss_value", "brier_score"],
}

# Severity bands of the diagnostic analyses, in order. A band label is built from the
# severities that fall into it, e.g. "mild_0.1_0.3" for the article grid (see analysis.py).
SEVERITY_BAND_NAMES: tuple[str, ...] = ("mild", "moderate", "severe")

# Zero-shot OOD regimes (reviewer block E): latent score S|Y and its exact Bayes posterior.
# Keys are the names written to reviewer_non_gaussian_ood_transfer.csv; every number used by
# simulation.generate_non_gaussian_baseline() lives here.
NON_GAUSSIAN_SPECS: dict[str, dict] = {
    "Bimodal Gaussian Mixture (2 subgroups in class 1)": {
        "kind": "bimodal_mixture",
        "neg": (-1.0, 0.90),  # (loc, scale) of class 0
        "pos_components": ((0.35, 0.60), (1.85, 0.70)),  # (loc, scale) of the two class-1 subgroups
        "pos_weight": 0.5,  # share of the first subgroup
    },
    "Heavy-Tailed Student-t (df=3, non-Gaussian tails)": {
        "kind": "student_t",
        "df": 3,
        "scale": 0.75,
        "loc0": -1.0,
        "loc1": 1.0,
    },
    "Heteroscedastic Gaussian (sigma0=0.65, sigma1=1.45)": {
        "kind": "heteroscedastic_gaussian",
        "neg": (-1.0, 0.65),
        "pos": (1.0, 1.45),
    },
}
NON_GAUSSIAN_DISTRIBUTIONS: list[str] = list(NON_GAUSSIAN_SPECS)

DEFAULT_RESULTS_DIR = "visionmetrics_stress_results_v3"

# Reproducibility links of the article, written to the reviewer audit and manuscript files.
# Format "Label: URL"; a run can override or clear them (StressTestConfig.public_links).
ARTICLE_PUBLIC_LINKS: tuple[str, ...] = (
    "GitHub: https://github.com/pavlo-bykovyy/vision-metrics",
    "Kaggle: https://www.kaggle.com/code/xrustya/v3visionmetrics-statistical-stress-test",
)


def _default_severities() -> np.ndarray:
    return np.round(np.linspace(0.0, 1.0, 11), 2)


@dataclass(frozen=True)
class StressTestConfig:
    """Simulation design. Defaults reproduce the final article run (308,000 rows)."""

    seed: int = DEFAULT_SEED
    n: int = 1000  # samples per replicate
    replicates: int = 1000  # Monte Carlo repetitions per prevalence
    prevalences: tuple[float, ...] = (0.50, 0.30, 0.10, 0.05)
    severities: np.ndarray = field(default_factory=_default_severities)

    # Calibrated baseline: S|Y=1 ~ N(+mu, sigma^2), S|Y=0 ~ N(-mu, sigma^2)
    mu: float = 1.0
    sigma: float = 1.0

    max_logit_bias: float = 4.0  # score-bias strength at lambda=1
    min_temperature: float = 0.40  # overconfidence endpoint
    max_temperature: float = 4.00  # underconfidence endpoint
    collapse_positive_target: float = 0.95  # p -> this value under collapse:positive
    collapse_negative_target: float = 0.05  # p -> this value under collapse:negative

    # Upper bounds of the "mild" and "moderate" severity bands (lambda <= bound)
    severity_mild_max: float = 0.3
    severity_moderate_max: float = 0.7

    # Zero-shot OOD transfer (reviewer block)
    ood_prevalences: tuple[float, ...] = (0.50, 0.30, 0.10)
    ood_replicates: int = 60
    ood_distributions: tuple[str, ...] = tuple(NON_GAUSSIAN_DISTRIBUTIONS)
    ood_crosscheck: bool = True  # independent re-computation of Table 11 (notebook's optional cell)

    cv_splits: int = 5
    n_boot: int = 1000

    # "Label: URL" entries for the reviewer audit / manuscript text; empty -> no links written
    public_links: tuple[str, ...] = ARTICLE_PUBLIC_LINKS

    @property
    def severity_band_edges(self) -> tuple[float, float]:
        return (self.severity_mild_max, self.severity_moderate_max)

    @property
    def nonzero_severities(self) -> list[float]:
        return [float(s) for s in self.severities if s > 0]
