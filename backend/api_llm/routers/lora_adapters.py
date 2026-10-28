import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from shared import schemas, models
from shared.dependencies import verify_token
from shared.database import get_db
from shared.config import UPLOAD_DIR
from api_llm.datasets.dataset_api_services import save_and_validate_zip
from shared.utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(prefix="/lora/adapters", tags=["LoRA Adapters"])


@router.get("/", response_model=schemas.LoraAdapterListResponse)
def get_lora_adapters(db: Session = Depends(get_db)):
    adapters = db.query(models.LoraAdapter).order_by(models.LoraAdapter.id.desc()).all()
    return {"adapters": adapters}

@router.post("/upload", response_model=schemas.LoraAdapterResponse)
async def upload_lora_zip(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)):
    """Upload a ZIP archive with an adapter, read the configuration, and save it to the database."""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    try:
        return save_and_validate_zip(file, db)
    except Exception as e:
        logger.warning(f"Failed to upload zip. Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process zip: {str(e)}")

@router.get("/{adapter_id}", response_model=schemas.LoraAdapterResponse)
def get_lora_adapter(
        adapter_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """Retrieve information about a specific adapter."""
    adapter = db.query(models.LoraAdapter).filter(models.LoraAdapter.id == adapter_id).first()
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")
    return adapter

@router.delete("/{adapter_id}")
async def delete_lora_adapter(adapter_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """Delete an adapter from the database and the file system."""
    adapter = db.query(models.LoraAdapter).filter(models.LoraAdapter.id == adapter_id).first()
    if not adapter:
        raise HTTPException(status_code=404, detail="Adapter not found")

    adapter_path = os.path.join(UPLOAD_DIR, adapter.folder_name)
    if os.path.exists(adapter_path):
        shutil.rmtree(adapter_path)

    db.delete(adapter)
    db.commit()
    return {"message": "Adapter successfully deleted"}