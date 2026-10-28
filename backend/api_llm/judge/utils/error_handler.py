from sqlalchemy.orm import Session
from shared.database import SessionLocal
from sqlalchemy.sql import func

from shared import models, enums
from shared.utils.logger import get_logger


logger = get_logger(__name__)


def handle_judge_error(db: Session, run_id: int, error: Exception) -> None:
    """
    Handles exceptions encountered during the LLM-as-a-Judge evaluation lifecycle.

    This function safely rolls back any pending database transactions to avoid
    corrupted states, logs the complete error traceback, and updates the status
    of the specific JudgeTaskRun to FAILED.

    Args:
        db (Session): The active SQLAlchemy database session.
        run_id (int): The unique identifier of the JudgeTaskRun.
        error (Exception): The exception object caught during execution.
    """
    logger.warning(f"[Judge Run {run_id}] ERROR during judge evaluation: {str(error)}", exc_info=True)
    db.rollback()

    try:
        run = db.query(models.JudgeTaskRun).filter(models.JudgeTaskRun.id == run_id).first()
        if run:
            run.status = enums.TaskStatus.FAILED
            run.error_message = str(error)
            db.commit()
    except Exception as db_error:
        logger.error(f"Failed to update task status to FAILED for run {run_id}: {db_error}")
        db.rollback()


def update_judge_run_to_failed(judge_task_run_id: int, error_msg: str) -> None:
    """
    Updates the status of a specific judge task run to 'FAILED' and saves the error message.

    This helper function is called when a fatal exception occurs during the
    judge evaluation process inside the worker (e.g., if the module fails to import).

    Args:
        judge_task_run_id (int): The unique identifier of the judge task run.
        error_msg (str): The description or representation of the error.
    """
    db = SessionLocal()
    try:
        run_record = db.query(models.JudgeTaskRun).filter(models.JudgeTaskRun.id == judge_task_run_id).first()

        if run_record:
            run_record.status = enums.TaskStatus.FAILED
            run_record.error_message = str(error_msg)
            db.commit()
            logger.info(f"Status updated to FAILED for judge_task_run_id: {judge_task_run_id}")
        else:
            logger.warning(f"Warning: JudgeTaskRun record {judge_task_run_id} NOT FOUND. Cannot update to FAILED.")

    except Exception as db_err:
        db.rollback()
        logger.error(f"Failed to update status to FAILED in database for judge_task_run_id {judge_task_run_id}: {db_err}")
    finally:
        db.close()