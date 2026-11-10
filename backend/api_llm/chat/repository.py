"""Database access for the chat worker. Returns plain dataclasses, never ORM objects."""
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from api_llm.schemas.chat import (
    AdapterConfig,
    AdapterNotFoundError,
    ChatJob,
    ChatRequestNotFoundError,
)
from shared import models as db_models
from shared.database import SessionLocal
from shared.enums import ActiveModelStatus


@contextmanager
def db_session() -> Iterator[Session]:
    """Short-lived session: rolls back on error and always closes."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_chat_job(chat_request_id: int) -> ChatJob:
    with db_session() as db:
        request = (
            db.query(db_models.ChatRequestRecord)
            .filter(db_models.ChatRequestRecord.id == chat_request_id)
            .first()
        )
        if request is None:
            raise ChatRequestNotFoundError(
                f"Chat request with ID {chat_request_id} not found."
            )
        return ChatJob(
            adapter_id=request.adapter_id,
            messages=request.messages,
            generation_params=request.generation_params or {},
        )


def save_chat_response(chat_request_id: int, answer: str) -> int:
    """Stores the generated answer and returns the new response ID."""
    with db_session() as db:
        record = db_models.ChatResponseRecord(request_id=chat_request_id, answer=answer)
        db.add(record)
        db.flush()
        response_id = record.id
        db.commit()
    return response_id


def get_adapter_config(adapter_id: int) -> AdapterConfig:
    with db_session() as db:
        adapter = (
            db.query(db_models.LoraAdapter)
            .filter(db_models.LoraAdapter.id == adapter_id)
            .first()
        )
        if adapter is None:
            raise AdapterNotFoundError(f"Adapter {adapter_id} not found in database.")
        return AdapterConfig(
            adapter_path=adapter.adapter_path,
            base_model_name_or_path=adapter.base_model_name_or_path,
            load_params=getattr(adapter, "load_params", None),
        )


def set_model_status(adapter_id: int, status: ActiveModelStatus) -> None:
    """Updates the status of the active model record (no-op if there is none)."""
    with db_session() as db:
        active_model = (
            db.query(db_models.ActiveModel)
            .filter(db_models.ActiveModel.adapter_id == adapter_id)
            .first()
        )
        if active_model is not None:
            active_model.status = status
            db.commit()
