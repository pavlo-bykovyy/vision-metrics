from fastapi import HTTPException
from sqlalchemy.orm import Session

from shared import schemas, models as db_models
from api_llm.services.chat_dispatcher_service import check_active_model_status, dispatch_chat_task_sync
from shared.utils.logger import get_logger

logger = get_logger(__name__)


def process_chat_generation(request: schemas.ChatRequest, db: Session) -> schemas.ChatResponse:
    """
    Processes the chat generation request.
    Looks up the model, verifies its active status, dispatches the background task,
    and formats the final response, translating internal errors into HTTPExceptions.

    Args:
        request (schemas.ChatRequest): The incoming request payload.
        db (Session): The active database session.

    Returns:
        schemas.ChatResponse: The structured response containing the generated text.

    Raises:
        HTTPException: If the model is not found, inactive, or generation fails.
    """
    adapter = db.query(db_models.LoraAdapter).filter(
        db_models.LoraAdapter.folder_name == request.model
    ).first()

    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{request.model}' not found in the database."
        )

    adapter_id = adapter.id

    try:
        active_model = check_active_model_status(db, adapter_id)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

    messages_dict = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        answer = dispatch_chat_task_sync(
            db=db,
            adapter_id=adapter_id,
            messages=messages_dict,
            generation_params= request.generation_params,
            queue_name=active_model.queue_name
        )
    except RuntimeError as run_err:
        raise HTTPException(status_code=500, detail=str(run_err))

    return schemas.ChatResponse(answer=answer, model=request.model)