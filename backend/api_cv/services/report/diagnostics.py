"""
Pure-Python diagnostics for a binary-classification metric profile.

No DB and no FastAPI imports, so it can be unit-tested without Postgres/Redis.
Rules follow the paper: metric *discordance* is flagged, and similarity to the
controlled failure signatures is reported as a hypothesis, never as a causal diagnosis.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

LN2 = math.log(2)  # log loss of a constant p=0.5 predictor
SEVERITY_ORDER = {"info": 0, "warning": 1, "critical": 2}

METRIC_KEYS = (
    "accuracy", "precision", "recall", "specificity", "f1", "balanced_accuracy",
    "mcc", "roc_auc", "pr_auc", "log_loss", "brier_score",
)

DISCLAIMER = (
    "Findings are diagnostic alerts based on metric discordance, not a causal diagnosis. "
    "Similarity to a controlled failure signature is a hypothesis: confirming it requires "
    "independent evidence (preprocessing, class mapping / score polarity, calibration, data shift). "
    "Baseline comparison is only meaningful on the same dataset, because prevalence changes "
    "most threshold-dependent metrics."
)


def _r(x: Optional[float]) -> Optional[float]:
    return None if x is None else round(float(x), 4)


@dataclass
class MetricProfile:
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    specificity: Optional[float] = None
    f1: Optional[float] = None
    balanced_accuracy: Optional[float] = None
    mcc: Optional[float] = None
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    log_loss: Optional[float] = None
    brier_score: Optional[float] = None
    tp: Optional[int] = None
    fp: Optional[int] = None
    tn: Optional[int] = None
    fn: Optional[int] = None
    threshold: float = 0.5

    @property
    def n(self) -> Optional[int]:
        parts = (self.tp, self.fp, self.tn, self.fn)
        return None if None in parts else sum(parts)

    @property
    def prevalence(self) -> Optional[float]:
        n = self.n
        return (self.tp + self.fn) / n if n else None

    @property
    def predicted_positive_rate(self) -> Optional[float]:
        n = self.n
        return (self.tp + self.fp) / n if n else None

    @classmethod
    def from_metric(cls, m: Any) -> "MetricProfile":
        """Build from the ORM `Metric` row (duck-typed: only attribute access)."""
        spec = None
        if m.tn is not None and m.fp is not None and (m.tn + m.fp) > 0:
            spec = m.tn / (m.tn + m.fp)
        elif m.balanced_accuracy is not None and m.recall is not None:
            spec = 2 * m.balanced_accuracy - m.recall  # BA = (recall + spec) / 2
        return cls(
            accuracy=m.accuracy, precision=m.precision, recall=m.recall,
            specificity=spec, f1=m.f1_score, balanced_accuracy=m.balanced_accuracy,
            mcc=m.mcc, roc_auc=m.roc_auc, pr_auc=m.pr_auc,
            log_loss=m.log_loss_value, brier_score=m.brier_score,
            tp=m.tp, fp=m.fp, tn=m.tn, fn=m.fn,
            threshold=m.decision_threshold if m.decision_threshold is not None else 0.5,
        )

    def vector(self) -> dict[str, Optional[float]]:
        return {k: _r(getattr(self, k)) for k in METRIC_KEYS}


@dataclass
class Finding:
    code: str
    severity: str  # info | warning | critical
    title: str
    evidence: dict[str, Any] = field(default_factory=dict)
    hint: str = ""


def analyze(p: MetricProfile) -> list[Finding]:
    out: list[Finding] = []

    # 1. Collapse to a single predicted class (paper: EfficientNetB4, Recall=1.0 but BA=0.5, MCC=0)
    ppr = p.predicted_positive_rate
    single_class = ppr is not None and (ppr >= 0.98 or ppr <= 0.02)
    if single_class:
        out.append(Finding(
            "SINGLE_CLASS_OUTPUT", "critical",
            "Model assigns (almost) all samples to one class",
            {"predicted_positive_rate": _r(ppr), "recall": _r(p.recall),
             "specificity": _r(p.specificity), "balanced_accuracy": _r(p.balanced_accuracy),
             "mcc": _r(p.mcc)},
            "Recall/F1 can look good while Balanced Accuracy ~0.5 and MCC ~0. "
            "Check the decision threshold, score saturation and preprocessing.",
        ))

    # 2. Strong asymmetry between classes (without full collapse)
    if (not single_class and p.recall is not None and p.specificity is not None
            and abs(p.recall - p.specificity) >= 0.4):
        out.append(Finding(
            "CLASS_ASYMMETRY", "warning",
            "Large gap between Recall and Specificity",
            {"recall": _r(p.recall), "specificity": _r(p.specificity)},
            "One class is detected much better than the other (collapse-like or score-bias-like behavior).",
        ))

    # 3. Ranking worse than random: usually polarity / class mapping problem
    if p.roc_auc is not None and p.roc_auc < 0.45:
        out.append(Finding(
            "INVERTED_RANKING", "critical",
            "ROC AUC is below chance level",
            {"roc_auc": _r(p.roc_auc), "mcc": _r(p.mcc)},
            "Check score polarity and class_mapping before concluding the architecture is weak.",
        ))

    # 4. Good ranking but poor hard decisions -> operating point / score shift candidate
    if (p.roc_auc is not None and p.balanced_accuracy is not None
            and p.roc_auc >= 0.70 and p.balanced_accuracy <= 0.60):
        out.append(Finding(
            "RANKING_DECISION_GAP", "warning",
            "Ranking is informative but thresholded decisions are poor",
            {"roc_auc": _r(p.roc_auc), "balanced_accuracy": _r(p.balanced_accuracy),
             "threshold": p.threshold},
            "Typical for an operating-point or score-shift problem; consider threshold review.",
        ))

    # 5. Probabilities worse than a constant 0.5 predictor: both Log Loss and Brier Score must
    #    exceed their constant baselines (paper, Section 4.6)
    ll_bad = p.log_loss is not None and p.log_loss > LN2
    br_bad = p.brier_score is not None and p.brier_score > 0.25
    if ll_bad and br_bad:
        out.append(Finding(
            "PROBABILITIES_WORSE_THAN_CONSTANT", "warning",
            "Probability quality is worse than predicting 0.5 for every sample",
            {"log_loss": _r(p.log_loss), "brier_score": _r(p.brier_score),
             "log_loss_constant_baseline": _r(LN2), "brier_constant_baseline": 0.25},
            "Possible miscalibration or overconfident wrong predictions.",
        ))

    # 6. Accuracy flatters the model under imbalance
    if (p.accuracy is not None and p.balanced_accuracy is not None
            and p.accuracy - p.balanced_accuracy >= 0.15):
        out.append(Finding(
            "ACCURACY_MASKING", "warning",
            "Accuracy is much higher than Balanced Accuracy",
            {"accuracy": _r(p.accuracy), "balanced_accuracy": _r(p.balanced_accuracy),
             "prevalence": _r(p.prevalence)},
            "Likely class imbalance; do not use Accuracy as the headline score.",
        ))

    # 7. High F1 with near-zero MCC
    if (p.mcc is not None and p.f1 is not None and abs(p.mcc) < 0.1 and p.f1 >= 0.6):
        out.append(Finding(
            "F1_MCC_DISCORDANCE", "warning",
            "F1 looks acceptable but MCC is near zero",
            {"f1": _r(p.f1), "mcc": _r(p.mcc)},
            "Positive-class metrics are not evidence of real two-class discrimination.",
        ))

    return out


def compare_to_baseline(cur: MetricProfile, base: MetricProfile) -> dict[str, Any]:
    """Deltas vs a baseline on the same dataset + similarity hypotheses (low confidence)."""
    deltas: dict[str, Optional[float]] = {}
    for k in METRIC_KEYS:
        a, b = getattr(cur, k), getattr(base, k)
        deltas[k] = None if a is None or b is None else _r(a - b)

    def mx(keys):
        vals = [abs(deltas[k]) for k in keys if deltas[k] is not None]
        return max(vals) if vals else None

    rank_move = mx(("roc_auc", "pr_auc"))
    dec_move = mx(("accuracy", "balanced_accuracy", "recall", "specificity"))
    prob_up = any(
        deltas[k] is not None and deltas[k] >= t
        for k, t in (("log_loss", 0.05), ("brier_score", 0.02))
    )
    rank_stable = rank_move is not None and rank_move < 0.02
    dec_stable = dec_move is not None and dec_move < 0.02

    cur_asym = abs(cur.recall - cur.specificity) if None not in (cur.recall, cur.specificity) else None
    base_asym = abs(base.recall - base.specificity) if None not in (base.recall, base.specificity) else None

    hyp: list[dict[str, str]] = []
    if deltas["roc_auc"] is not None and deltas["roc_auc"] <= -0.3:
        hyp.append({"similar_to": "score_inversion",
                    "why": "ROC AUC dropped sharply together with other families"})
    elif rank_move is not None and rank_move >= 0.02 and None not in (cur_asym, base_asym) \
            and cur_asym - base_asym >= 0.3:
        hyp.append({"similar_to": "class_collapse",
                    "why": "ranking degraded and Recall/Specificity asymmetry grew"})
    if rank_stable and dec_move is not None and dec_move >= 0.05:
        hyp.append({"similar_to": "score_bias",
                    "why": "ROC AUC/AP unchanged while hard decisions moved (operating-point shift)"})
    if rank_stable and dec_stable and prob_up:
        hyp.append({"similar_to": "calibration_drift",
                    "why": "ranking and decisions unchanged while Log Loss/Brier increased"})

    for h in hyp:
        h["confidence"] = "low"
    return {"deltas": deltas, "hypotheses": hyp}


def build_report(meta: dict[str, Any], cur: MetricProfile,
                 baseline_meta: Optional[dict[str, Any]] = None,
                 base: Optional[MetricProfile] = None) -> dict[str, Any]:
    findings = analyze(cur)
    worst = max((SEVERITY_ORDER[f.severity] for f in findings), default=0)
    status = {0: "ok", 1: "warning", 2: "critical"}[worst]

    report: dict[str, Any] = {
        "meta": meta,
        "status": status,
        "profile": {
            "metrics": cur.vector(),
            "confusion": {"tp": cur.tp, "fp": cur.fp, "tn": cur.tn, "fn": cur.fn},
            "n": cur.n,
            "prevalence": _r(cur.prevalence),
            "predicted_positive_rate": _r(cur.predicted_positive_rate),
            "threshold": cur.threshold,
        },
        "findings": [asdict(f) for f in findings],
        "baseline": None,
        "disclaimer": DISCLAIMER,
    }
    if base is not None:
        report["baseline"] = {"meta": baseline_meta, **compare_to_baseline(cur, base)}
    return report
