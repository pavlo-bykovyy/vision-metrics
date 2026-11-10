from sqlalchemy.orm import joinedload

from shared.database import engine
from shared.utils.logger import get_logger
from api_llm.services.celery_app import celery_app
from api_llm.judge.utils.error_handler import update_judge_run_to_failed
from api_llm.queues import JUDGE_EVALUATION_QUEUE

logger = get_logger(__name__)


@celery_app.task(bind=True,
                 name="llm.judge.evaluation",
                 queue=JUDGE_EVALUATION_QUEUE)
def worker_judge_evaluate(self, judge_task_run_id: int):
    """
    Background worker function to process a specific LLM-as-a-Judge run.
    Delegates the execution to the core judge logic module.
    """
    logger.info(f"Judge Worker received task run ID: {judge_task_run_id}")

    try:
        engine.dispose()

        # ---------------------------------------------------------
        # CRITICAL: LOCAL IMPORT
        # We import the logic ONLY when the worker actually runs the task.
        # This prevents the main API thread from loading heavy dependencies.
        # ---------------------------------------------------------
        from api_llm.judge.task import run_judge_evaluation_task

        # Execute the database and evaluation logic for this specific judge run
        run_judge_evaluation_task(judge_task_run_id=judge_task_run_id)

    except Exception as e:
        logger.warning(f"Judge Worker failed to start or load module for run {judge_task_run_id}: {e}")
        update_judge_run_to_failed(judge_task_run_id, str(e))
    finally:
        from api_llm.utils.memory import clear_cuda_cache
        clear_cuda_cache()