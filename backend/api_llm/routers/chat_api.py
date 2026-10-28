from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from shared import schemas, models as db_models
from shared.database import get_db
from shared.enums import ActiveModelStatus
from api_llm.services import chat_api_service

router = APIRouter(prefix="/lora/chat", tags=["Custom Chat API"])


@router.get("/models", response_model=schemas.ModelsListResponse)
def get_available_models(db: Session = Depends(get_db)):
    """
    Retrieves a list of all currently active and ready models.
    This endpoint allows the external Java system to know which models
    are currently loaded in memory and available for text generation.

    Args:
        db (Session): The active database session.

    Returns:
        dict: A dictionary containing a list of SimpleModelInfo objects.
    """
    active_models = db.query(db_models.ActiveModel).filter(
        db_models.ActiveModel.status.in_([
            ActiveModelStatus.CREATED,
            ActiveModelStatus.STARTING,
            ActiveModelStatus.READY
        ])
    ).all()

    data = [
        schemas.SimpleModelInfo(id=str(am.adapter_id), name=am.adapter.folder_name)
        for am in active_models
    ]

    return {"data": data}


@router.post("/generate", response_model=schemas.ChatResponse)
def generate_chat_response(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Receives a chat prompt from an external system, resolves the adapter by name,
    validates its active status, dispatches the task, logs history, and returns the answer.
    """
    return chat_api_service.process_chat_generation(request=request, db=db)
