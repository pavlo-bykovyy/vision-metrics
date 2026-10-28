from sqlalchemy.orm import Session
from shared import enums
from shared import models as db_models
from api_llm.services.celery_app import celery_app
from shared.utils.logger import get_logger

logger = get_logger(__name__)


def check_active_model_status(db: Session, adapter_id: int):
    """
    Checks if a specific model is marked as active and ready in the database.

    Args:
        db (Session): The active database session used to run the query.
        adapter_id (int): The unique identifier of the model (adapter) to check.

    Returns:
        db_models.ActiveModel: The active model record if found.

    Raises:
        ValueError: If the model is not active or not ready.
    """
    active_record = db.query(db_models.ActiveModel).filter(
        db_models.ActiveModel.adapter_id == adapter_id,
        db_models.ActiveModel.status.in_([
            enums.ActiveModelStatus.CREATED,
            enums.ActiveModelStatus.STARTING,
            enums.ActiveModelStatus.READY
        ])
    ).first()

    if not active_record:
        raise ValueError(f"Model {adapter_id} is not active or not ready.")

    return active_record


def dispatch_chat_task_sync(
        db: Session,
        adapter_id: int,
        messages: list,
        queue_name: str,
        generation_params: dict | None = None,
) -> str:
    """
    Dispatches a chat generation task to a specific Celery queue, waits for
    the result synchronously, and records both the request and response in the database.

    Args:
        db (Session): The active SQLAlchemy database session.
        adapter_id (int): The unique identifier of the model adapter.
        messages (list): The list of formatted chat messages.
        queue_name (str): The name of the Celery queue to dispatch to.
        generation_params (dict | None, optional): Additional keyword arguments to control
            the text generation (e.g., max_tokens, temperature). Defaults to None.

    Returns:
        str: The generated text answer from the model.

    Raises:
        RuntimeError: If database saving fails or text generation times out.
    """
    chat_request = db_models.ChatRequestRecord(
        adapter_id=adapter_id,
        messages=messages,
        generation_params=generation_params
    )

    try:
        db.add(chat_request)
        db.commit()
        db.refresh(chat_request)
    except Exception as db_err:
        db.rollback()
        logger.warning(f"Failed to save chat request to database: {db_err}")
        raise RuntimeError(f"Database error while saving request history: {db_err}")

    try:
        async_result = celery_app.send_task(
            name="chat.generate_text",
            queue=queue_name,
            kwargs={"chat_request_id": chat_request.id}
        )

        logger.info(f"Dispatched chat task to queue '{queue_name}' with Task ID: {async_result.id}")

        response_id = async_result.get(timeout=600.0)

        chat_response = db.query(db_models.ChatResponseRecord).filter(
            db_models.ChatResponseRecord.id == response_id
        ).first()

        if not chat_response:
            raise RuntimeError(f"Chat response with ID {response_id} not found in database.")

        return chat_response.answer

    except Exception as e:
        logger.warning(f"Text generation failed or timed out: {e}")

        try:
            error_response = db_models.ChatResponseRecord(
                request_id=chat_request.id,
                answer=f"ERROR: {str(e)}"
            )
            db.add(error_response)
            db.commit()
        except Exception as log_err:
            db.rollback()
            logger.warning(f"Failed to log error response to database: {log_err}")

        raise RuntimeError(f"Text generation failed or timed out: {e}")