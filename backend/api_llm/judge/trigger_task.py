"""
This module orchestrates the background processing of judge evaluations.
It handles dispatching tasks to Celery and managing failure states.
"""

from shared.utils.logger import get_logger

from api_llm.services.celery_app import celery_app


logger = get_logger(__name__)


def trigger_judge_task(judge_task_run_id: int) -> str:
    """
    Dispatches the judge evaluation task to the Celery queue for background processing.

    Args:
        judge_task_run_id (int): The database ID of the judge task run.

    Returns:
        str: The unique Celery task ID generated for this job.
    """
    try:
        async_result = celery_app.send_task(
            name="llm.judge.evaluation",
            queue="judge_tasks",
            kwargs={"judge_task_run_id": judge_task_run_id}
        )

        logger.info(f"Successfully dispatched judge_task_run_id={judge_task_run_id} to Celery queue. Task ID: {async_result.id}")

        return async_result.id

    except Exception as e:
        logger.warning(f"Failed to dispatch Celery task for judge_task_run_id={judge_task_run_id}: {e}", exc_info=True)
        raise RuntimeError(f"Queue dispatch error: {e}")