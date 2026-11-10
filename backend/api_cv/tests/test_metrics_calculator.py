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
