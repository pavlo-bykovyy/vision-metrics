"""
Model State Manager Service.

This standalone script is responsible for cleaning up stuck active model statuses
in the database after an unexpected system reboot or crash, as well as restarting
any background evaluation tasks that were interrupted.
"""

from shared.database import SessionLocal
from shared import models as db_models
from shared.enums import ActiveModelStatus, TaskStatus
from shared.utils.logger import get_logger
from api_llm.services.evaluation_service import trigger_evaluation_task


logger = get_logger(__name__)


def reset_stuck_models(db):
    """
    Finds all active models stuck in STARTING or READY states,
    and resets their statuses to STOPPED.
    """
    logger.info("Starting State Manager: Cleaning up stuck active model statuses...")
    try:
        stuck_models = db.query(db_models.ActiveModel).filter(
            db_models.ActiveModel.status.in_([
                ActiveModelStatus.STARTING,
                ActiveModelStatus.READY
            ])
        ).all()

        for model in stuck_models:
            model.status = ActiveModelStatus.STOPPED
            logger.info(f"Status for active model {model.adapter_id} reset to STOPPED.")

        db.commit()
        logger.info(f"Active models cleanup completed. Changed status for {len(stuck_models)} models.")
    except Exception as e:
        logger.warning(f"Error during active models status cleanup: {e}")
        db.rollback()


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


def run_state_manager():
    """
    Main entry point for the state manager script.
    """
    db = SessionLocal()
    try:
        reset_stuck_models(db)
        restart_stuck_evaluations(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_state_manager()