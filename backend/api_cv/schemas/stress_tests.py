"""
Pydantic schemas of the statistical stress-test API (`/stress-tests`).

Defaults mirror `api_cv.services.stress_test.config.StressTestConfig`. That package imports
scipy/scikit-learn and belongs to the CV worker, so the values are duplicated here and kept in
sync by `api_cv/tests/test_stress_test_api.py::test_schema_defaults_match_stress_test_config`.
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from shared.enums import TaskStatus


StressTestStep = Literal["simulate", "reviewer", "figures", "archive"]
FigureFormat = Literal["png", "pdf", "svg"]

STEP_ORDER: tuple[str, ...] = ("simulate", "reviewer", "figures", "archive")

FAILURE_PATH_LABELS: list[str] = [
    "collapse:positive",
    "collapse:negative",
    "score_bias:positive",
    "score_bias:negative",
    "calibration_drift:over",
    "calibration_drift:under",
    "score_inversion:none",
]

# Keys of stress_test.config.NON_GAUSSIAN_SPECS (zero-shot OOD regimes).
OOD_DISTRIBUTIONS: list[str] = [
    "Bimodal Gaussian Mixture (2 subgroups in class 1)",
    "Heavy-Tailed Student-t (df=3, non-Gaussian tails)",
    "Heteroscedastic Gaussian (sigma0=0.65, sigma1=1.45)",
]

# Mirrors stress_test.config.ARTICLE_PUBLIC_LINKS.
ARTICLE_PUBLIC_LINKS: list[str] = [
    "GitHub: https://github.com/pavlo-bykovyy/vision-metrics",
    "Kaggle: https://www.kaggle.com/code/xrustya/v3visionmetrics-statistical-stress-test",
]

PLATFORM_METRICS: list[str] = [
    "accuracy", "precision", "recall", "f1_score", "mcc", "balanced_accuracy",
    "roc_auc", "pr_auc", "log_loss_value", "brier_score",
]


class StressTestConfigSchema(BaseModel):
    """Simulation design; the defaults reproduce the final article run (308,000 rows)."""

    seed: int = Field(20260822, ge=0)
    n: int = Field(1000, ge=50, le=100_000, description="Samples per replicate")
    replicates: int = Field(1000, ge=2, le=10_000, description="Monte Carlo repetitions per prevalence")
    prevalences: list[float] = Field(default_factory=lambda: [0.50, 0.30, 0.10, 0.05], min_length=1)
    severity_levels: int = Field(11, ge=2, le=51, description="Evenly spaced severities in [0, 1]")

    mu: float = Field(1.0, gt=0)
    sigma: float = Field(1.0, gt=0)
    max_logit_bias: float = Field(4.0, gt=0)
    min_temperature: float = Field(0.40, gt=0, lt=1)
    max_temperature: float = Field(4.00, gt=1)
    collapse_positive_target: float = Field(0.95, gt=0.5, le=1, description="Target probability of collapse:positive")
    collapse_negative_target: float = Field(0.05, ge=0, lt=0.5, description="Target probability of collapse:negative")

    severity_mild_max: float = Field(0.3, gt=0, lt=1, description="Upper bound of the 'mild' severity band")
    severity_moderate_max: float = Field(0.7, gt=0, lt=1, description="Upper bound of the 'moderate' severity band")

    ood_prevalences: list[float] = Field(default_factory=lambda: [0.50, 0.30, 0.10], min_length=1)
    ood_replicates: int = Field(60, ge=1, le=10_000)
    ood_distributions: list[str] = Field(default_factory=lambda: list(OOD_DISTRIBUTIONS), min_length=1)
    ood_crosscheck: bool = Field(True, description="Independently recompute the OOD table as a consistency check")

    cv_splits: int = Field(5, ge=2, le=20)
    n_boot: int = Field(1000, ge=10, le=100_000)

    public_links: list[str] = Field(
        default_factory=lambda: list(ARTICLE_PUBLIC_LINKS),
        max_length=10,
        description="'Label: URL' lines written to the reviewer audit and manuscript files; empty list = none",
    )

    @field_validator("public_links")
    @classmethod
    def _check_public_links(cls, values: list[str]) -> list[str]:
        links = [v.strip() for v in values if v and v.strip()]
        if any(len(v) > 500 or "\n" in v for v in links):
            raise ValueError("each public link must be a single line of at most 500 characters")
        return links

    @field_validator("prevalences", "ood_prevalences")
    @classmethod
    def _check_prevalences(cls, values: list[float]) -> list[float]:
        if any(not 0 < v < 1 for v in values):
            raise ValueError("prevalences must lie strictly between 0 and 1")
        if len(set(values)) != len(values):
            raise ValueError("prevalences must be unique")
        return values

    @field_validator("ood_distributions")
    @classmethod
    def _check_ood_distributions(cls, values: list[str]) -> list[str]:
        unknown = [v for v in values if v not in OOD_DISTRIBUTIONS]
        if unknown:
            raise ValueError(f"unknown OOD distributions: {unknown}; allowed: {OOD_DISTRIBUTIONS}")
        return [v for v in OOD_DISTRIBUTIONS if v in set(values)]

    @model_validator(mode="after")
    def _check_folds(self):
        if self.replicates < self.cv_splits:
            raise ValueError("replicates must be >= cv_splits (GroupKFold groups by replicate)")
        if self.severity_mild_max >= self.severity_moderate_max:
            raise ValueError("severity_mild_max must be < severity_moderate_max")
        return self


class StressTestCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    config: StressTestConfigSchema = Field(default_factory=StressTestConfigSchema)
    steps: list[StressTestStep] = Field(default_factory=lambda: list(STEP_ORDER))
    figure_formats: list[FigureFormat] = Field(default_factory=lambda: ["png"], min_length=1)
    figure_dpi: int = Field(300, ge=72, le=600)

    @field_validator("steps")
    @classmethod
    def _normalize_steps(cls, steps: list[str]) -> list[str]:
        if "simulate" not in steps:
            raise ValueError("'simulate' is required: every other step reads its outputs")
        return [s for s in STEP_ORDER if s in set(steps)]


class StressTestRun(BaseModel):
    id: int
    name: Optional[str] = None
    status: TaskStatus
    stage: Optional[str] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    config: dict
    steps: list[str]
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    has_archive: bool = False

    model_config = ConfigDict(from_attributes=True)


class StressTestPaginationResponse(BaseModel):
    items: list[StressTestRun]
    total: int
    page: int
    size: int
    pages: int


class StressTestFile(BaseModel):
    path: str
    kind: Literal["table", "figure", "text", "other"]
    size_bytes: int


class StressTestTable(BaseModel):
    name: str
    columns: list[str]
    rows: list[list]
    total_rows: int
    truncated: bool


class StressTestDefaults(BaseModel):
    config: StressTestConfigSchema
    steps: list[str]
    figure_formats: list[str]
    figure_dpi: int
    failure_paths: list[str]
    platform_metrics: list[str]
    ood_distributions: list[str]
