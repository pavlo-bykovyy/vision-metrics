from sqlalchemy.orm import joinedload

from shared.database import engine
from shared.utils.logger import get_logger
from api_llm.services.celery_app import celery_app
from api_llm.services.utils import update_status_to_failed


logger = get_logger(__name__)


@celery_app.task(bind=True, name="llm.evaluation", queue="llm_tasks")
def worker_evaluate(self, evaluation_task_id: int):
    """
    Main worker function.
    Fetches data, delegates ML operations, and saves the results.
    """
    logger.info(f"Worker started for evaluation_task_id: {evaluation_task_id}")

    try:
        engine.dispose()

        # # ---------------------------------------------------------
        # # CRITICAL: LOCAL IMPORT
        # # We import the ML logic ONLY when the worker actually runs the task.
        # # This prevents the API from crashing due to missing TensorFlow.
        # # ---------------------------------------------------------
        from api_llm.evaluation.tasks import run_evaluation_task
        #
        # # Execute heavy logic
        run_evaluation_task(task_id=evaluation_task_id)


    except Exception as e:
        logger.warning(f"Worker failed for evaluation_task_id {evaluation_task_id}: {e}")
        update_status_to_failed(evaluation_task_id, str(e))
