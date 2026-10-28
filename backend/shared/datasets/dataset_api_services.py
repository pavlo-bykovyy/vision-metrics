import os
import uuid
from typing import Optional, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from shared import models, schemas, enums
from shared.config import UPLOAD_DIR
from shared.utils.logger import get_logger

from shared.datasets.dataset_core import (
    check_dataset_name_exists,
    create_artifact_record,
    validate_image_folder_dataset,
    validate_columns_exist,
    get_dataset_columns
)
from shared.datasets.file_utils import save_upload_file_to_disk


logger = get_logger(__name__)


async def create_dataset_service(db: Session, file: UploadFile, form_data: schemas.DatasetCreateForm) -> models.Dataset:
    """
    Orchestrates dataset creation: verifies name uniqueness, stores file, validates contents,
    and registers Artifact and Dataset records. Handles HTTP Exceptions.
    """
    logger.info(f"Starting dataset creation process for dataset name: {form_data.name}")

    try:
        check_dataset_name_exists(db, form_data.name)

        file_path = await save_upload_file_to_disk(file, UPLOAD_DIR)

        validate_dataset_file(file_path, form_data)

        new_artifact = create_artifact_record(db, file.filename, file_path)
        new_dataset = create_dataset_record(db, form_data, new_artifact.id)

        logger.info(f"Dataset creation complete. Returning dataset ID: {new_dataset.id}")
        return new_dataset

    except ValueError as e:
        logger.error(f"Validation error during dataset creation: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.warning(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


def create_dataset_record(db: Session, form_data: schemas.DatasetCreateForm, artifact_id: Optional[int] = None) -> models.Dataset:
    """Creates, commits, and refreshes a new Dataset record linked to an Artifact."""
    logger.info(f"Starting Dataset creation for Artifact ID: {artifact_id}")
    try:
        new_dataset = models.Dataset(
            name=form_data.name,
            artifact_id=artifact_id,
            dataset_type=form_data.dataset_type,
            file_source=form_data.file_source,
            file_format=form_data.file_format,
            source_url=form_data.source_url,
            id_column=form_data.id_column,
            schema_config=form_data.schema_config,
            mapping_config=form_data.mapping_config,
        )
        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)
        logger.info(f"Dataset successfully saved! ID: {new_dataset.id}")
        return new_dataset
    except Exception as e:
        logger.warning(f"DATABASE ERROR (Dataset) during record creation! Detail: {str(e)}")
        db.rollback()
        raise


def validate_tabular_dataset(file_path: str, form_data: schemas.DatasetCreateForm) -> None:
    """Validates that required columns exist in the uploaded tabular dataset."""
    logger.info("Dataset format identified as tabular. Validating dataset columns.")

    columns = get_dataset_columns(file_path, form_data.file_format)
    cleaned_columns = [col.strip().lstrip('\ufeff') for col in columns]

    required_cols = []

    if getattr(form_data, 'id_column', None):
        required_cols.append(form_data.id_column.strip())

    if getattr(form_data, 'schema_config', None):
        schema = form_data.schema_config

        input_fields = schema.get("input_fields", [])
        target_fields = schema.get("target_fields", [])
        metadata_fields = schema.get("metadata_fields", [])

        for field in input_fields + target_fields + metadata_fields:
            if field and field.strip():
                required_cols.append(field.strip())

    if not required_cols:
        logger.info("No specific columns required for validation. Skipping.")
        return

    validate_columns_exist(cleaned_columns, required_cols)
    logger.info("Tabular column validation successful.")


def validate_dataset_file(file_path: str, form_data: schemas.DatasetCreateForm) -> None:
    """Dispatches file validation based on format and ensures cleanup if validation fails."""
    try:
        if form_data.file_format == enums.DatasetFormat.IMAGE_FOLDER:
            validate_image_folder_dataset(file_path)
        else:
            validate_tabular_dataset(file_path, form_data)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.warning(f"Cleaned up physical file after validation failure: {file_path}")
        raise


def update_dataset_service(db: Session, dataset_id: int, update_data: schemas.DatasetUpdateRequest) -> models.Dataset:
    """Updates metadata (like name or columns) for an existing dataset."""
    dataset = get_dataset_by_id_service(db, dataset_id)

    if update_data.name and update_data.name != dataset.name:
        existing = db.query(models.Dataset).filter(models.Dataset.name == update_data.name).first()
        if existing:
            raise ValueError("Dataset with this name already exists")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(dataset, key, value)

    db.commit()
    db.refresh(dataset)
    return dataset