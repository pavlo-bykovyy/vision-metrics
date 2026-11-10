from shared import models as db_models
from shared.enums import ActiveModelStatus
from shared.utils.logger import get_logger

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
