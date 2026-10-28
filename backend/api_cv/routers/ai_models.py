import math
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from shared import models, schemas
from api_cv.services import services
from shared.database import get_db
from shared.dependencies import verify_token
from shared.utils.logger import get_logger


logger = get_logger("AI-MODEL-ROUTER")

router = APIRouter(tags=["AI Models"])


@router.get("/models/{model_id}", response_model=schemas.ModelDetail)
def get_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Retrieve a specific AI model by its ID.
    Includes all associated evaluations and their metrics.
    """
    db_model = db.query(models.Model) \
        .options(joinedload(models.Model.evaluations).joinedload(models.Evaluation.metrics)) \
        .filter(models.Model.id == model_id) \
        .first()

    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    return db_model


@router.get("/models/", response_model=schemas.ModelPaginationResponse)
def get_models(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        current_user: dict = Depends(verify_token)
):
    """
    Retrieve a paginated list of all AI models.
    Includes the history of evaluations for each model.
    """
    offset = (page - 1) * size
    total_count = db.query(models.Model).count()

    items = db.query(models.Model) \
        .options(joinedload(models.Model.evaluations).joinedload(models.Evaluation.metrics)) \
        .order_by(models.Model.id.desc()) \
        .offset(offset) \
        .limit(size) \
        .all()

    return {
        "items": items,
        "total": total_count,
        "page": page,
        "size": size,
        "pages": math.ceil(total_count / size) if total_count > 0 else 1
    }


@router.post("/upload-file/", response_model=schemas.ArtifactResponse)
async def upload_file(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Upload a physical file (e.g., model architecture, weights, or dataset).
    Saves the file to the server and creates an Artifact record in the database.
    """
    try:
        new_name, path = services.save_upload_file(file)
        db_file = models.Artifact(filename=new_name, file_path=path)

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return db_file
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-model/", response_model=schemas.ModelDetail)
async def create_model(
        data: schemas.ModelCreateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Register a new classical ML model in the system.
    Links the provided architecture and weights artifacts to the new model.
    """
    db_model = models.Model(
        name=data.name,
        description=data.description,
        arch_file_id=data.arch_id,
        weights_file_id=data.weights_id,
        class_mapping=data.class_mapping
    )

    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    return db_model


@router.patch("/models/{model_id}", response_model=schemas.ModelDetail)
async def update_model(
        model_id: int,
        update_data: schemas.ModelUpdateRequest,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Update an existing AI model's information (like name or description).
    """
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()

    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)

    return db_model


@router.delete("/models/{model_id}")
async def delete_model(
        model_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(verify_token)
):
    """
    Delete a specific AI model from the database.
    """
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()

    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(db_model)
    db.commit()

    return {"message": f"Model {model_id} successfully deleted"}
