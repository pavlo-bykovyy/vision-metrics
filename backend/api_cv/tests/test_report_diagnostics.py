"""Pure unit tests: no DB, no Redis, no GPU. Values come from Table 12 of the paper."""
import numpy as np
import pandas as pd

from api_cv.services.report.diagnostics import MetricProfile, analyze, build_report, compare_to_baseline
from api_cv.services.report.probe_experiments import (
    compute_group_stats,
    normalize_diagnostic_dataframe,
)


def _codes(profile):
    return {f.code for f in analyze(profile)}


def test_efficientnet_b4_single_class_collapse():
    p = MetricProfile(accuracy=0.543, precision=0.543, recall=1.0, specificity=0.0, f1=0.704,
                      balanced_accuracy=0.5, mcc=0.0, roc_auc=0.682, pr_auc=0.716,
                      tp=700, fp=589, tn=0, fn=0)
    codes = _codes(p)
    assert "SINGLE_CLASS_OUTPUT" in codes
    assert "RANKING_DECISION_GAP" not in codes  # roc_auc 0.682 < 0.70
    assert "F1_MCC_DISCORDANCE" in codes
    assert build_report({"evaluation_id": 1}, p)["status"] == "critical"


def test_meso4_inverted_ranking():
    p = MetricProfile(accuracy=0.390, precision=0.459, recall=0.681, f1=0.548,
                      balanced_accuracy=0.363, mcc=-0.346, roc_auc=0.243, pr_auc=0.407)
    assert "INVERTED_RANKING" in _codes(p)


def test_mobilenet_v2_is_not_flagged_as_collapse():
    p = MetricProfile(accuracy=0.597, precision=0.808, recall=0.337, f1=0.476,
                      balanced_accuracy=0.621, mcc=0.288, roc_auc=0.752, pr_auc=0.750)
    assert "SINGLE_CLASS_OUTPUT" not in _codes(p)


def test_specificity_is_derived_from_ba_when_confusion_missing():
    class M:  # minimal stand-in for the ORM Metric row
        accuracy = precision = f1_score = mcc = roc_auc = pr_auc = None
        log_loss_value = brier_score = None
        recall, balanced_accuracy = 0.9, 0.6
        tp = fp = tn = fn = None
        decision_threshold = 0.5

    assert abs(MetricProfile.from_metric(M).specificity - 0.3) < 1e-9


def test_baseline_calibration_drift_hypothesis():
    base = MetricProfile(accuracy=0.84, recall=0.84, specificity=0.84, balanced_accuracy=0.84,
                         roc_auc=0.92, pr_auc=0.92, log_loss=0.40, brier_score=0.12)
    cur = MetricProfile(accuracy=0.84, recall=0.84, specificity=0.84, balanced_accuracy=0.84,
                        roc_auc=0.92, pr_auc=0.92, log_loss=0.55, brier_score=0.16)
    hyp = compare_to_baseline(cur, base)["hypotheses"]
    assert [h["similar_to"] for h in hyp] == ["calibration_drift"]


def test_probe_experiments_normalize_and_group_stats():
    df = pd.DataFrame({
        "degradation_class": ["collapse:positive", "score_bias:negative"],
        "group_id": [1, 2],
        "lambda": [0.1, 0.2],
        "accuracy": [0.54, 0.60],
        "precision": [0.54, 0.80],
        "recall": [1.0, 0.30],
        "f1_score": [0.70, 0.44],
        "mcc": [0.0, 0.28],
        "balanced_accuracy": [0.5, 0.60],
        "roc_auc": [0.68, 0.75],
        "pr_auc": [0.71, 0.75],
        "log_loss_value": [0.69, 0.55],
        "brier_score": [0.25, 0.19],
    })
    norm = normalize_diagnostic_dataframe(df)
    assert "f1" in norm.columns
    assert "log_loss" in norm.columns
    assert "specificity_derived" in norm.columns
    assert abs(norm.loc[0, "specificity_derived"] - 0.0) < 1e-9
    assert abs(norm.loc[1, "specificity_derived"] - 0.9) < 1e-9

    y_true = np.array(["a", "a", "b", "b"])
    y_pred = np.array(["a", "b", "b", "b"])
    groups = np.array([1, 1, 2, 2])
    grp_scores, ci_low, ci_high = compute_group_stats(y_true, y_pred, groups, n_boot=200)
    assert list(grp_scores) == [0.5, 1.0]
    assert 0.5 <= ci_low <= ci_high <= 1.0

