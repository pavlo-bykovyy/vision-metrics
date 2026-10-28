from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from shared import schemas
from shared.database import get_db
from shared.dependencies import verify_token
from shared.datasets.dataset_api_services import (
    create_dataset_service,
    update_dataset_service,
)
from shared.datasets.dataset_core import (
    get_all_datasets_service,
    get_dataset_by_id_service,
    delete_dataset_service
)

router = APIRouter(tags=["Datasets"])


@router.post("/datasets/", response_model=schemas.DatasetDetail)
async def create_dataset(
        file: UploadFile = File(...),
        form_data: schemas.DatasetCreateForm = Depends(),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    return await create_dataset_service(db, file, form_data)

@router.get("/datasets/", response_model=List[schemas.DatasetDetail])
def get_datasets(db: Session = Depends(get_db),
                 current_user: dict = Depends(verify_token)):
    return get_all_datasets_service(db)

@router.get("/datasets/{dataset_id}", response_model=schemas.DatasetDetail)
def get_dataset(dataset_id: int,
                db: Session = Depends(get_db),
                current_user: dict = Depends(verify_token)):
    return get_dataset_by_id_service(db, dataset_id)

@router.patch("/datasets/{dataset_id}", response_model=schemas.DatasetDetail)
def update_dataset(
        dataset_id: int,
        update_data: schemas.DatasetUpdateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    return update_dataset_service(db, dataset_id, update_data)

@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int,
                   db: Session = Depends(get_db),
                   current_user: dict = Depends(verify_token)):
    return delete_dataset_service(db, dataset_id)