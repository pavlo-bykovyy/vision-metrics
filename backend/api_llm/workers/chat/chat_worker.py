"""
Celery tasks of the LLM worker.

Kept deliberately thin: tasks only wire the repository (DB) to the
ModelManager (GPU) and to the inference code.
"""
from api_llm.evaluation.inference_core import generate_single_completion
from api_llm.lora.model_loader import load_models
from api_llm.lora.utils import extract_adapter_zip_for_task
from api_llm.services.celery_app import celery_app
from api_llm.chat import repository
from api_llm.chat.model_manager import ModelManager
from shared.config import UPLOAD_DIR
from shared.utils.logger import get_logger

logger = get_logger(__name__)

model_manager = ModelManager(
    get_adapter_config=repository.get_adapter_config,
    set_status=repository.set_model_status,
    extract_adapter=lambda adapter_path: extract_adapter_zip_for_task(
        adapter_path, UPLOAD_DIR
    ),
    load_models=load_models,
)


@celery_app.task(name="chat.generate_text")
def task_generate_chat_response(chat_request_id: int) -> int:
    """
    Generates an answer for a stored chat request and saves it.

    Returns:
        ID of the created ChatResponseRecord.

    Raises:
        ChatRequestNotFoundError (ValueError): if the request does not exist.
    """
    job = repository.get_chat_job(chat_request_id)

    with model_manager.acquire(job.adapter_id) as loaded:
        answer = generate_single_completion(
            model=loaded.model,
            tokenizer=loaded.tokenizer,
            messages=job.messages,
            generation_params=job.generation_params,
        )

    return repository.save_chat_response(chat_request_id, answer)


@celery_app.task(name="model.warm_up")
def task_warm_up_model(adapter_id: int) -> bool:
    """Preloads the model so the first chat request has no cold-start latency."""
    logger.info(f"Starting warm-up for adapter_id: {adapter_id}")
    model_manager.warm_up(adapter_id)
    logger.info(f"Warm-up completed successfully for adapter_id: {adapter_id}")
    return True


@celery_app.task(name="model.unload")
def task_unload_model() -> bool:
    """Unloads the current model from GPU/RAM and frees memory."""
    logger.info("Starting memory cleanup on worker...")
    if model_manager.unload():
        logger.info("Model unloaded successfully. VRAM is cleared.")
    else:
        logger.info("No model was loaded in memory. Nothing to clean.")
    return True