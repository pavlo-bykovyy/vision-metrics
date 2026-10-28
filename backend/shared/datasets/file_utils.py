import os
import uuid
from fastapi import UploadFile, HTTPException

from shared.utils.logger import get_logger


logger = get_logger(__name__)


async def save_upload_file_to_disk(file: UploadFile, upload_dir: str) -> str:
    """
    Generates a unique filename and asynchronously saves the uploaded file to disk in chunks.

    This method reads the file in small chunks to prevent high RAM consumption,
    making it safe for uploading large AI datasets or model weights.

    Args:
        file (UploadFile): The file uploaded by the user via FastAPI.
        upload_dir (str): Directory path on disk where the file should be saved.

    Returns:
        str: Absolute physical file path of the saved file.
    """
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    safe_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(upload_dir, safe_filename)

    logger.info(f"Saving uploaded physical file in chunks to: {file_path}")

    with open(file_path, "wb") as buffer:
        chunk_size = 1024 * 1024

        while chunk := await file.read(chunk_size):
            buffer.write(chunk)

    return file_path
