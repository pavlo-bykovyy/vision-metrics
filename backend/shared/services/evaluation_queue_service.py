"""
evaluation_queue_service.py

This module orchestrates the background processing of model evaluations.
It handles saving tasks to the database queue, dispatching them to Celery,
and managing failure states.
"""

from shared.utils.logger import get_logger
from api_cv.services.celery_app import celery_app


logger = get_logger(__name__)


def trigger_evaluation_task(evaluation_id: int) -> str:
    """
    Dispatches the evaluation task to the Celery queue for background processing.

    Args:
        evaluation_id (int): The database ID of the evaluation.

    Returns:
        str: The unique Celery task ID generated for this job.
    """
    try:
        async_result = celery_app.send_task(
            name="cv.evaluation",
            queue="cv_tasks",
            kwargs={"evaluation_id": evaluation_id}
        )
        logger.info(f"Successfully dispatched evaluation_id={evaluation_id} to Celery queue. Task ID: {async_result.id}")

        return async_result.id

    except Exception as e:
        logger.warning(f"Failed to dispatch Celery task for evaluation_id={evaluation_id}: {e}", exc_info=True)
        raise RuntimeError(f"Queue dispatch error: {e}")
