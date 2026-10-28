import shutil
from fastapi import APIRouter, Depends

from shared import schemas
from shared.dependencies import verify_token

router = APIRouter(tags=["System Info"])

@router.get("/storage-info/", response_model=schemas.StorageInfo)
def get_storage_info(token: str = Depends(verify_token)):
    total, used, free = shutil.disk_usage("/")
    gb = 1024 ** 3
    percentage = int(round((used / total) * 100)) if total > 0 else 0
    return {
        "total": round(total / gb, 1),
        "used": round(used / gb, 1),
        "free": round(free / gb, 1),
        "percentage": percentage,
        "unit": "GB"
    }