from shared import models as db_models
from shared.enums import TaskStatus
from shared.utils.logger import get_logger
from api_llm.services.evaluation_service import trigger_evaluation_task

logger = get_logger(__name__)


def restart_stuck_evaluations(db):
    """
    Finds all evaluation tasks stuck in active states (PENDING, DOWNLOADING, EVALUATING)
    and re-dispatches them to the Celery queue.
    """
    logger.info("Starting State Manager: Restarting interrupted evaluation tasks...")
    try:
        stuck_tasks = db.query(db_models.EvaluationTask).filter(
            db_models.EvaluationTask.status.in_([
                TaskStatus.PENDING,
                TaskStatus.DOWNLOADING,
                TaskStatus.EVALUATING
            ])
        ).all()

        restarted_count = 0
        for task in stuck_tasks:
            try:
                task.status = TaskStatus.PENDING
                task.error = None

                new_celery_task_id = trigger_evaluation_task(evaluation_task_id=task.id)
                task.celery_task_id = new_celery_task_id

                logger.info(f"Successfully re-dispatched evaluation task {task.id}. New Celery ID: {new_celery_task_id}")
                restarted_count += 1
            except Exception as trigger_err:
                task.status = TaskStatus.FAILED
                task.error = f"Failed to restart after system crash: {trigger_err}"
                logger.error(f"Failed to restart task {task.id}: {trigger_err}")

        db.commit()
        logger.info(f"Evaluation tasks restart completed. Restarted {restarted_count} tasks.")
    except Exception as e:
        logger.warning(f"Error during evaluation tasks restart: {e}")
        db.rollback()
