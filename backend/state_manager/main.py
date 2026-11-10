"""
Model State Manager Service.

This standalone script is responsible for cleaning up stuck active model statuses
in the database after an unexpected system reboot or crash, as well as restarting
any background evaluation tasks that were interrupted.
"""

from shared.database import SessionLocal
from state_manager.services.active_models import reset_stuck_models
from state_manager.services.evaluations import restart_stuck_evaluations


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
