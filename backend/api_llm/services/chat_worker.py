import os
import shutil
import torch
import gc
from api_llm.services.celery_app import celery_app
from api_llm.evaluation.inference_core import generate_single_completion
from api_llm.lora.model_loader import load_models
from api_llm.lora.utils import extract_adapter_zip_for_task
from shared.config import UPLOAD_DIR
from shared.database import SessionLocal
from shared import models as db_models
from shared.enums import ActiveModelStatus
from shared.utils.logger import get_logger

logger = get_logger(__name__)

worker_cache = {
    "adapter_id": None,
    "tokenizer": None,
    "base_model": None,
    "model": None,
    "temp_extract_dir": None
}


def _update_model_status(adapter_id: int, new_status: ActiveModelStatus):
    """
    Connects to the database and safely updates the status of the active model worker.
    """
    db = SessionLocal()
    try:
        active_model = db.query(db_models.ActiveModel).filter(
            db_models.ActiveModel.adapter_id == adapter_id
        ).first()

        if active_model:
            active_model.status = new_status
            db.commit()
    finally:
        db.close()


def _load_model_if_needed(adapter_id: int):
    """
    Loads the model into GPU/RAM if it is not already loaded by this worker process.
    Updates the database lifecycle statuses and clears VRAM, but leaves extracted files on disk.
    """
    if worker_cache.get("adapter_id") == adapter_id:
        return

    logger.info(f"Worker is initializing model: {adapter_id}")

    _update_model_status(adapter_id, ActiveModelStatus.STARTING)

    if worker_cache.get("model") is not None:
        del worker_cache["model"]
        del worker_cache["base_model"]
        del worker_cache["tokenizer"]
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    db = SessionLocal()
    try:
        adapter = db.query(db_models.LoraAdapter).filter(db_models.LoraAdapter.id == adapter_id).first()
        if not adapter:
            raise ValueError(f"Adapter {adapter_id} not found in database.")

        temp_extract_dir, actual_model_dir = extract_adapter_zip_for_task(adapter.adapter_path, UPLOAD_DIR)

        load_params = getattr(adapter, "load_params", {})
        if load_params is None:
            load_params = {
                "torch_dtype": "bfloat16",
                "quantization": "4bit",
                "device_map": "auto",
                "use_fast_tokenizer": False,
            }

        tokenizer, base_model, model = load_models(
            base_model_name=adapter.base_model_name_or_path,
            adapter_dir=actual_model_dir,
            load_params=load_params
        )

        worker_cache["adapter_id"] = adapter_id
        worker_cache["tokenizer"] = tokenizer
        worker_cache["base_model"] = base_model
        worker_cache["model"] = model

        worker_cache["temp_extract_dir"] = temp_extract_dir

        _update_model_status(adapter_id, ActiveModelStatus.READY)

    except Exception as e:
        logger.warning(f"Failed to load model {adapter_id}: {e}")
        _update_model_status(adapter_id, ActiveModelStatus.ERROR)
        raise e
    finally:
        db.close()


@celery_app.task(bind=True, name="chat.generate_text")
def task_generate_chat_response(self, chat_request_id: int) -> str:
    """
    Background task for text generation using a language model.

    Retrieves the chat request from the database using the provided ID,
    extracts necessary generation parameters, ensures the model is loaded,
    and generates the response.

    Args:
        chat_request_id (int): The unique identifier of the chat request.

    Returns:
        str: The generated text response.

    Raises:
        ValueError: If the chat request is not found in the database.
    """
    db = SessionLocal()

    try:
        chat_request = db.query(db_models.ChatRequestRecord).filter(
            db_models.ChatRequestRecord.id == chat_request_id
        ).first()

        if not chat_request:
            raise ValueError(f"Chat request with ID {chat_request_id} not found.")

        adapter_id = chat_request.adapter_id
        messages = chat_request.messages
        generation_params = chat_request.generation_params or {}

        _load_model_if_needed(adapter_id)

        tokenizer = worker_cache["tokenizer"]
        model = worker_cache["model"]

        answer = generate_single_completion(
            model=model,
            tokenizer=tokenizer,
            messages=messages,
            generation_params=generation_params
        )

        chat_response = db_models.ChatResponseRecord(
            request_id=chat_request.id,
            answer=answer
        )
        db.add(chat_response)
        db.commit()

        return chat_response.id

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


@celery_app.task(bind=True, name="model.warm_up")
def task_warm_up_model(self, adapter_id: int):
    """
    Background task to preload the model into GPU/RAM.

    This acts as a 'warm-up' request so that the first actual
    chat generation request doesn't suffer from cold-start latency.
    """

    logger.info(f"Starting warm-up for adapter_id: {adapter_id}")
    try:
        _load_model_if_needed(adapter_id)
        logger.info(f"Warm-up completed successfully for adapter_id: {adapter_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to warm up model {adapter_id}: {e}")
        raise e


@celery_app.task(bind=True, name="model.unload")
def task_unload_model(self):
    """
    Background task to unload the current model from GPU/RAM and free up memory.
    """

    logger.info("Starting memory cleanup on worker...")

    if worker_cache.get("model") is not None:
        del worker_cache["model"]
        del worker_cache["base_model"]
        del worker_cache["tokenizer"]

        worker_cache["adapter_id"] = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Model unloaded successfully. VRAM is cleared.")
    else:
        logger.info("No model was loaded in memory. Nothing to clean.")

    return True