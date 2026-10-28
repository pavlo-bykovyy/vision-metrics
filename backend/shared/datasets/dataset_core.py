import os
import csv
import json
from typing import Iterator
import zipfile
import pandas as pd
from sqlalchemy.orm import Session

from shared import models, enums
from shared.utils.logger import get_logger


logger = get_logger(__name__)


def get_dataset_columns(file_path: str, file_format: enums.DatasetFormat) -> list[str]:
    """Reads the first few rows of a dataset file to extract its column names."""
    if file_format == enums.DatasetFormat.CSV:
        df = pd.read_csv(file_path, nrows=0)
        return df.columns.tolist()
    elif file_format == enums.DatasetFormat.JSONL:
        df = pd.read_json(file_path, lines=True, nrows=1)
        return df.columns.tolist()
    raise ValueError(f"Unsupported file format: {file_format}")


def validate_columns_exist(columns: list[str], required_columns: list[str]) -> None:
    """Validates that all required columns exist in the dataset."""
    missing = [col for col in required_columns if col and col not in columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def check_dataset_name_exists(db: Session, name: str) -> None:
    """Validates that the provided dataset name is unique in the database."""
    existing = db.query(models.Dataset).filter(models.Dataset.name == name).first()
    if existing:
        logger.warning(f"Dataset creation aborted. Dataset name '{name}' already exists.")
        raise ValueError("Dataset with this name already exists")


def validate_image_folder_dataset(file_path: str) -> None:
    """Validates that the file uploaded for IMAGE_FOLDER format is a valid ZIP archive."""
    logger.info("Dataset format identified as IMAGE_FOLDER. Validating ZIP archive structure.")
    if not zipfile.is_zipfile(file_path):
        logger.warning(f"Validation failed. File at {file_path} is not a valid ZIP archive.")
        raise ValueError("Uploaded file must be a valid ZIP archive for IMAGE_FOLDER format.")
    logger.info("ZIP archive validation successful.")


def create_artifact_record(db: Session, original_filename: str, file_path: str) -> models.Artifact:
    """Creates and flushes a new Artifact entity in the database."""
    logger.info("Creating and flushing new Artifact database record.")
    new_artifact = models.Artifact(filename=original_filename, file_path=file_path)
    db.add(new_artifact)
    db.flush()
    return new_artifact


def get_all_datasets_service(db: Session) -> list[models.Dataset]:
    """Retrieves all datasets from the database."""
    return db.query(models.Dataset).order_by(models.Dataset.id.desc()).all()


def get_dataset_by_id_service(db: Session, dataset_id: int) -> models.Dataset:
    """Retrieves a specific dataset by its ID."""
    dataset = db.query(models.Dataset).filter(models.Dataset.id == dataset_id).first()
    if not dataset:
        raise ValueError("Dataset not found")
    return dataset


def delete_dataset_service(db: Session, dataset_id: int) -> dict:
    """Deletes a dataset and its associated physical file (Artifact)."""
    dataset = get_dataset_by_id_service(db, dataset_id)

    if dataset.file_artifact and os.path.exists(dataset.file_artifact.file_path):
        try:
            os.remove(dataset.file_artifact.file_path)
        except Exception:
            pass
        db.delete(dataset.file_artifact)

    db.delete(dataset)
    db.commit()
    return {"message": "Dataset successfully deleted"}
