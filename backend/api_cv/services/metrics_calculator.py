import os
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
    matthews_corrcoef, balanced_accuracy_score,
    brier_score_loss, log_loss,
    average_precision_score
)
from shared.utils.logger import get_logger
from shared.models import PredictionResult

logger = get_logger(__name__)


def calculate_metrics(prediction_result: 'PredictionResult',
                      last_dim: int,
                      weights_path: str) -> dict:
    """
    Calculates classification metrics based on the provided PredictionResult object.

    Args:
        prediction_result (PredictionResult): Object containing y_true, y_pred_probs, and processing time.
        last_dim (int): The dimension of the last layer (1 for binary classification, >1 for multi-class).
        weights_path (str): Path to the model weights (used to calculate model size).

    Returns:
        dict: A dictionary containing the calculated metrics.
    """
    logger.info("Calculating metrics...")

    y_true = prediction_result.y_true
    y_pred_probs = prediction_result.y_pred_probs
    processing_time = prediction_result.processing_time_ms

    if len(y_true) == 0:
        raise ValueError("The dataset is empty. Cannot calculate metrics.")

    mean_latency = processing_time / len(y_true)
    weights_size = os.path.getsize(weights_path) if os.path.exists(weights_path) else 0

    if last_dim == 1:
        y_pred = (y_pred_probs > 0.5).astype(int).flatten()
        y_score = y_pred_probs.flatten()
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        avg_type = 'binary'
    else:
        y_pred = np.argmax(y_pred_probs, axis=1)
        y_score = y_pred_probs
        tn, fp, fn, tp = 0, 0, 0, 0
        avg_type = 'macro'

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average=avg_type, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average=avg_type, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, average=avg_type, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "mean_latency_ms": round(float(mean_latency), 4),
        "model_size_bytes": int(weights_size),
        "averaging_mode": avg_type,
        "decision_threshold": 0.5,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "class_mapping": prediction_result.class_mapping
    }

    try:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_score, multi_class='ovr' if last_dim > 1 else 'raise'))
    except ValueError:
        metrics["roc_auc"] = None

    try:
        metrics["pr_auc"] = float(average_precision_score(y_true, y_score, average='macro' if last_dim > 1 else None))
    except Exception:
        metrics["pr_auc"] = None

    try:
        metrics["log_loss_value"] = float(log_loss(y_true, y_pred_probs))
    except Exception:
        metrics["log_loss_value"] = None

    if last_dim == 1:
        try:
            metrics["brier_score"] = float(brier_score_loss(y_true, y_score))
        except Exception:
            metrics["brier_score"] = None
    else:
        metrics["brier_score"] = None

    logger.info("Metrics successfully calculated.")
    return metrics