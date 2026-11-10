"""
api_llm/judge/worker.py

Contains Celery background tasks for judging and scoring LLM evaluations.
"""
import time

from api_llm import queues as q
from api_llm.services.celery_app import celery_app

from shared.database import engine
from shared.utils.logger import get_logger
from api_llm.judge.utils.error_handler import update_judge_run_to_failed

logger = get_logger(__name__)


@celery_app.task(bind=True, name=q.ATTACK_JUDGE_TASK, queue=q.ATTACK_JUDGE_QUEUE)
def worker_attack_judge_evaluate(self, judge_task_run_id: int):
    """
    Celery worker task for evaluating attack runs using LLM-as-a-Judge.

    Performs canary checks, runs judge scoring models, and calculates
    the Attack Success Rate (ASR).

    Args:
        self: The task instance itself (injected via bind=True).
        judge_task_run_id (int): The unique identifier for the judge evaluation run.
    """
    logger.info(f"Attack Judge Worker received run ID: {judge_task_run_id}")
    started = time.monotonic()

    try:
        engine.dispose()

        from api_llm.attacks.attack_judge import run_attack_judging

        run_attack_judging(judge_task_run_id)
        logger.info(
            f"Attack Judge Worker finished run {judge_task_run_id} in {time.monotonic() - started:.0f}s"
        )

    except Exception as e:
        logger.warning(
            f"Attack Judge Worker catastrophically failed for run {judge_task_run_id} "
            f"after {time.monotonic() - started:.0f}s: {e}"
        )
        update_judge_run_to_failed(judge_task_run_id, str(e))
    finally:
        from api_llm.utils.memory import clear_cuda_cache
        clear_cuda_cache()