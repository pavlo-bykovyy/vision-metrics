import os
import uuid
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from fastapi import UploadFile

from shared import models
from shared.config import UPLOAD_DIR
from api_llm.lora.utils import extract_adapter_config_from_zip
from shared.utils.logger import get_logger


logger = get_logger(__name__)


def save_upload_file(upload_file: UploadFile, destination_path: str) -> None:
    """
    Saves an uploaded file stream to the specified local disk path.
    """
    try:
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


def save_and_validate_zip(upload_file: UploadFile, db: Session) -> models.LoraAdapter:
    """
    Processes an uploaded ZIP archive containing a LoRA adapter.

    Generates a unique filename, saves the archive to the upload directory,
    extracts metadata from the nested configuration file, and persists the
    adapter metadata to the database. Rolls back and cleans up on failure.

    Returns:
        models.LoraAdapter: The newly created database record.

    Raises:
        RuntimeError: If file processing, validation, or database transaction fails.
    """
    base_name = os.path.splitext(upload_file.filename)[0]
    unique_id = uuid.uuid4().hex[:6]
    saved_filename = f"{base_name}_{unique_id}.zip"
    zip_path = os.path.join(UPLOAD_DIR, saved_filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    save_upload_file(upload_file, zip_path)

    try:
        config_data = extract_adapter_config_from_zip(zip_path)

        task_type = config_data.get("task_type")
        base_model = config_data.get("base_model_name_or_path")

        new_adapter = models.LoraAdapter(
            folder_name=saved_filename,
            adapter_path=zip_path,
            task_type=task_type,
            base_model_name_or_path=base_model
        )

        db.add(new_adapter)
        db.commit()
        db.refresh(new_adapter)

        return new_adapter

    except Exception as e:
        logger.warning("ZIP validation or processing error: %s", e, exc_info=True)

        if os.path.exists(zip_path):
            os.remove(zip_path)

        db.rollback()
        raise RuntimeError(f"Failed to process ZIP file: {e}")