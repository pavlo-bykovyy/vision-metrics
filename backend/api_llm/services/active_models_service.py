import uuid
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from shared import models as db_models, schemas
from shared.enums import ActiveModelStatus
from api_llm.services.celery_app import celery_app


STATIC_QUEUE_NAME = "chat_tasks"


def create_active_model(db: Session, request: schemas.ActiveModelStartRequest) -> db_models.ActiveModel:
    """
    CREATE: Registers a new active model and assigns it to the chat Celery queue.
    Enforces a strict limit of ONLY ONE active model at a time.
    """
    adapter = db.query(db_models.LoraAdapter).filter(db_models.LoraAdapter.id == request.adapter_id).first()

    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found in the database.")

    existing = db.query(db_models.ActiveModel).filter(
        db_models.ActiveModel.adapter_id == request.adapter_id
    ).first()

    if existing:
        return existing

    currently_active = db.query(db_models.ActiveModel).filter(
        db_models.ActiveModel.status.in_([
            ActiveModelStatus.CREATED,
            ActiveModelStatus.STARTING,
            ActiveModelStatus.READY
        ])
    ).first()

    if currently_active:
        raise HTTPException(
            status_code=400,
            detail=f"Only one active model is allowed at a time. Model {currently_active.adapter_id} is currently active. Please stop it first."
        )

    new_active_model = db_models.ActiveModel(
        adapter_id=request.adapter_id,
        queue_name=STATIC_QUEUE_NAME,
        status=ActiveModelStatus.CREATED
    )

    db.add(new_active_model)
    db.commit()
    db.refresh(new_active_model)

    celery_app.send_task(
        name="model.warm_up",
        queue=new_active_model.queue_name,
        kwargs={"adapter_id": new_active_model.adapter_id}
    )

    return new_active_model


def get_all_active_models(db: Session) -> List[db_models.ActiveModel]:
    """
    READ ALL: Retrieves a list of all active models from the database.
    """
    return db.query(db_models.ActiveModel).all()


def get_active_model_by_adapter(db: Session, adapter_id: int) -> db_models.ActiveModel:
    """
    READ ONE: Retrieves specific active model details by its adapter ID.
    """
    active_model = db.query(db_models.ActiveModel).filter(
        db_models.ActiveModel.adapter_id == adapter_id
    ).first()

    if not active_model:
        raise HTTPException(status_code=404, detail="Active model not found.")

    return active_model


def update_active_model_status(db: Session, adapter_id: int, update_data: schemas.ActiveModelStatusUpdateRequest) -> db_models.ActiveModel:
    """
    UPDATE: Manually changes the status of an active model (e.g., forcing it to STOPPED or ERROR).
    """
    active_model = get_active_model_by_adapter(db, adapter_id)

    active_model.status = update_data.status
    db.commit()
    db.refresh(active_model)

    return active_model


def delete_active_model(db: Session, adapter_id: int) -> dict:
    """
    DELETE: Removes an active model record from the database
    and triggers a background task to clear the worker's RAM/VRAM.
    """
    active_model = get_active_model_by_adapter(db, adapter_id)

    if not active_model:
        return {"message": "Active model not found."}

    queue_name = active_model.queue_name

    db.delete(active_model)
    db.commit()

    celery_app.send_task(
        name="model.unload",
        queue=queue_name
    )

    return {
        "message": f"Active model for adapter {adapter_id} successfully stopped, removed from DB, and memory cleanup triggered."
    }