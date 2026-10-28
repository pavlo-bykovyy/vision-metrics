from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared import schemas
from shared.database import get_db
from api_llm.services import active_models_service


router = APIRouter(prefix="/lora/active-models", tags=["Active Models Management"])


@router.post("/", response_model=schemas.ActiveModelResponse)
def create_active_model(request: schemas.ActiveModelStartRequest, db: Session = Depends(get_db)):
    """
    CREATE: Register a new active model and assign it a Celery queue.
    """
    return active_models_service.create_active_model(db=db, request=request)


@router.get("/", response_model=List[schemas.ActiveModelResponse])
def read_all_active_models(db: Session = Depends(get_db)):
    """
    READ: Get a list of all registered active models and their current statuses.
    """
    return active_models_service.get_all_active_models(db=db)


@router.get("/{adapter_id}", response_model=schemas.ActiveModelResponse)
def read_active_model(adapter_id: int, db: Session = Depends(get_db)):
    """
    READ: Get details for a specific active model by its adapter ID.
    """
    return active_models_service.get_active_model_by_adapter(db=db, adapter_id=adapter_id)


@router.patch("/{adapter_id}/status", response_model=schemas.ActiveModelResponse)
def update_active_model(
        adapter_id: int,
        update_data: schemas.ActiveModelStatusUpdateRequest,
        db: Session = Depends(get_db)
):
    """
    UPDATE: Modify the status of an active model manually.
    """
    return active_models_service.update_active_model_status(db=db, adapter_id=adapter_id, update_data=update_data)


@router.delete("/{adapter_id}")
def delete_active_model(adapter_id: int, db: Session = Depends(get_db)):
    """
    DELETE: Remove an active model from the system.
    """
    return active_models_service.delete_active_model(db=db, adapter_id=adapter_id)