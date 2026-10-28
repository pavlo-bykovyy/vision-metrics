"""
worker.py

This file is responsible for heavy machine learning computations and
independently saving the evaluation results to the database.
"""

from sqlalchemy.orm import joinedload

from shared.database import SessionLocal, engine
from shared import models, enums
from shared.utils.logger import get_logger
from api_cv.services.celery_app import celery_app


logger = get_logger(__name__)


def _update_status_to_evaluating(evaluation_id: int):
    """
    Updates the status of a specific evaluation record to 'EVALUATING' in the database.

    This helper function is intended to be called at the beginning of the
    evaluation worker process to notify the system that the task execution
    has started.

    Args:
        evaluation_id (int): The unique identifier of the evaluation record
                             to be updated.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        eval_record = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()

        if eval_record:
            eval_record.status = enums.TaskStatus.EVALUATING
            db.commit()
            logger.info(f"Status updated to EVALUATING for evaluation_id: {evaluation_id}")
        else:
            logger.warning(f"Warning: Evaluation record {evaluation_id} NOT FOUND. Cannot update to EVALUATING.")

    except Exception as e:
        db.rollback()
        logger.warning(f"Failed to update status to evaluating: {e}")
    finally:
        db.close()


def _update_status_to_failed(evaluation_id: int, error_msg: str):
    """
    Updates the status of a specific evaluation record to 'FAILED' and saves the error message.

    This helper function is called when an exception occurs during the
    evaluation process inside the worker.

    Args:
        evaluation_id (int): The unique identifier of the evaluation record.
        error_msg (str): The description or representation of the error.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        eval_record = db.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()

        if eval_record:
            eval_record.status = enums.TaskStatus.FAILED
            eval_record.error_message = str(error_msg)[:255]
            db.commit()
            logger.info(f"Status updated to FAILED for evaluation_id: {evaluation_id}")
        else:
            logger.warning(f"Warning: Evaluation record {evaluation_id} NOT FOUND. Cannot update to FAILED.")

    except Exception as db_err:
        db.rollback()
        logger.error(f"Failed to update status to failed in database: {db_err}")
    finally:
        db.close()


def _fetch_evaluation_data(evaluation_id: int) -> dict:
    """
    Step 1: Fetches paths and configuration for the evaluation from the database.
    """
    logger.info("Step 1: Fetching evaluation data from DB...")
    db = SessionLocal()
    try:
        evaluation = db.query(models.Evaluation).options(
            joinedload(models.Evaluation.model).joinedload(models.Model.architecture),
            joinedload(models.Evaluation.model).joinedload(models.Model.weights),
            joinedload(models.Evaluation.dataset).joinedload(models.Dataset.file_artifact)
        ).filter(models.Evaluation.id == evaluation_id).first()

        if not evaluation:
            raise RuntimeError(f"Evaluation {evaluation_id} not found in DB")

        if not evaluation.model.architecture or not evaluation.model.weights:
            raise ValueError("Model architecture or weights artifact is missing in DB.")
        if not evaluation.dataset.file_artifact:
            raise ValueError("Dataset file artifact is missing in DB.")

        logger.info(f"Evaluation data loaded. Dataset ID: {evaluation.dataset.id}")

        db.expunge(evaluation)
        return evaluation

    finally:
        db.close()


def _save_results(evaluation_id: int, raw_metrics: dict):
    """
    Step 4: Formats metrics and saves them to the database, updating the evaluation status.
    """
    logger.info("Step 4: Saving results to database...")
    db_save = SessionLocal()
    try:
        processed_metrics = {
            "accuracy": round(raw_metrics['accuracy'], 4),
            "precision": round(raw_metrics['precision'], 4),
            "recall": round(raw_metrics['recall'], 4),
            "f1_score": round(raw_metrics['f1_score'], 4),
            "roc_auc": round(raw_metrics['roc_auc'], 4) if raw_metrics.get('roc_auc') is not None else None,
            "mcc": round(raw_metrics['mcc'], 4) if raw_metrics.get('mcc') is not None else None,
            "balanced_accuracy": round(raw_metrics['balanced_accuracy'], 4) if raw_metrics.get('balanced_accuracy') is not None else None,
            "pr_auc": round(raw_metrics['pr_auc'], 4) if raw_metrics.get('pr_auc') is not None else None,
            "log_loss_value": round(raw_metrics['log_loss_value'], 4) if raw_metrics.get('log_loss_value') is not None else None,
            "brier_score": round(raw_metrics['brier_score'], 4) if raw_metrics.get('brier_score') is not None else None,
            "mean_latency_ms": raw_metrics.get('mean_latency_ms'),
            "model_size_bytes": raw_metrics.get('model_size_bytes'),
            "averaging_mode": raw_metrics.get('averaging_mode', 'binary'),
            "decision_threshold": raw_metrics.get('decision_threshold', 0.5),
            "tp": raw_metrics['tp'],
            "fp": raw_metrics['fp'],
            "tn": raw_metrics['tn'],
            "fn": raw_metrics['fn'],
            "class_mapping": raw_metrics.get('class_mapping')
        }

        db_metrics = models.Metric(evaluation_id=evaluation_id, **processed_metrics)
        db_save.add(db_metrics)

        eval_record = db_save.query(models.Evaluation).filter(models.Evaluation.id == evaluation_id).first()
        if eval_record:
            eval_record.status = enums.TaskStatus.COMPLETED

        db_save.commit()
        logger.info(f"Worker successfully saved metrics for evaluation_id: {evaluation_id}")

    except Exception as e:
        logger.warning(f"Database error: Failed to save metrics for evaluation_id {evaluation_id}. Details: {repr(e)}")
        db_save.rollback()
        raise e
    finally:
        db_save.close()


@celery_app.task(bind=True, name="cv.evaluation", queue="cv_tasks")
def worker_evaluate(self, evaluation_id: int):
    """
    Main worker function.
    Fetches data, delegates ML operations, and saves the results.
    """
    logger.info(f"Worker started for evaluation_id: {evaluation_id}")

    try:
        engine.dispose()

        _update_status_to_evaluating(evaluation_id)
        evaluation_record = _fetch_evaluation_data(evaluation_id)

        def is_cancelled():
            db.refresh(evaluation_record)
            if evaluation_record.status == enums.TaskStatus.CANCELLED:
                return True
            return False

        # ---------------------------------------------------------
        # CRITICAL: LOCAL IMPORT
        # We import the ML logic ONLY when the worker actually runs the task.
        # This prevents the API from crashing due to missing TensorFlow.
        # ---------------------------------------------------------
        from api_cv.services.ml_executor import load_and_evaluate_model

        # Execute heavy logic
        raw_metrics = load_and_evaluate_model(
            evaluation=evaluation_record,
            cancel_check_callback=is_cancelled
        )

        _save_results(evaluation_id, raw_metrics)

    except Exception as e:
        logger.warning(f"Worker failed for evaluation_id {evaluation_id}: {e}")
        _update_status_to_failed(evaluation_id, str(e))
