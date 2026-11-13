"""Platform metrics: log loss is defined even when the dataset contains a single class."""
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("sklearn")

from api_cv.services.metrics_calculator import calculate_metrics  # noqa: E402


def _result(y_true, probs):
    return SimpleNamespace(
        y_true=np.asarray(y_true),
        y_pred_probs=np.asarray(probs, dtype=float),
        processing_time_ms=10.0,
        class_mapping=None,
    )


def test_binary_single_class_log_loss():
    m = calculate_metrics(_result([1, 1, 1], [[0.9], [0.8], [0.6]]), last_dim=1, weights_path="/nonexistent")
    assert m["log_loss_value"] == pytest.approx(-np.mean(np.log([0.9, 0.8, 0.6])))
    assert m["roc_auc"] is None  # undefined with one class


def test_multiclass_missing_class_log_loss():
    probs = [[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]]
    m = calculate_metrics(_result([0, 1], probs), last_dim=3, weights_path="/nonexistent")
    assert m["log_loss_value"] == pytest.approx(-np.mean(np.log([0.7, 0.8])))


def test_binary_softmax_two_outputs_matches_sigmoid():
    y = [0, 1, 1, 0, 1]
    p1 = np.array([0.2, 0.7, 0.4, 0.6, 0.9])
    sigmoid = calculate_metrics(_result(y, p1[:, None]), last_dim=1, weights_path="/nonexistent")
    softmax = calculate_metrics(_result(y, np.stack([1 - p1, p1], axis=1)), last_dim=2, weights_path="/nonexistent")
    assert softmax["averaging_mode"] == "binary"
    assert softmax["brier_score"] is not None
    assert (softmax["tn"], softmax["fp"], softmax["fn"], softmax["tp"]) == (1, 1, 1, 2)
    for key, value in sigmoid.items():
        if isinstance(value, float):
            assert softmax[key] == pytest.approx(value), key
        else:
            assert softmax[key] == value, key
