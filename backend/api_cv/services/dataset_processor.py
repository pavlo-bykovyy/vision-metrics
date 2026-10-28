import os
import csv
import zipfile
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from sqlalchemy.orm import Session

from shared import models, enums
from shared.utils.logger import get_logger
from shared.exceptions import TaskCancelledError
from api_cv.services.zip_image_loader import process_zip_in_batches


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


def get_predictions(evaluation: models.Evaluation,
                    model,
                    target_size: tuple,
                    batch_size: int,
                    cancel_check_callback=None,
                    preprocess_fn=None):
    """
    Loads the dataset (ZIP or CSV) and returns the true labels, model predictions,
    and dynamically generated class mapping.
    Uses tf.data.Dataset for multi-threaded, fast image loading in tabular format.
    """
    dataset = evaluation.dataset
    dataset_path = dataset.file_artifact.file_path
    start_time = time.perf_counter()

    model_class_mapping = evaluation.model.class_mapping
    class_mapping = None

    if dataset.file_format == enums.DatasetFormat.IMAGE_FOLDER:
        logger.info("IMAGE_FOLDER format detected. Using ZIP batch processing...")
        return process_zip_in_batches(
            evaluation=evaluation,
            target_size=target_size,
            model=model,
            batch_size=batch_size
        )
    else:
        logger.info("Tabular format detected. Loading images via optimized tf.data pipeline...")

        schema_config = dataset.schema_config or {}
        input_fields = schema_config.get("input_fields", [])
        target_fields = schema_config.get("target_fields", [])

        if not input_fields or not target_fields:
            raise ValueError("Input fields or Target fields are not defined in the dataset's schema_config.")

        prompt_column = input_fields[0]
        target_column = target_fields[0]

        df = pd.read_csv(dataset_path)
        if prompt_column not in df.columns or target_column not in df.columns:
            raise KeyError(f"Required columns not found in CSV. Available columns: {list(df.columns)}")

        raw_labels = df[target_column].astype(str).values
        unique_dataset_classes = set(raw_labels)

        if model_class_mapping:
            logger.info(f"Using class mapping from the Model: {model_class_mapping}")
            class_mapping = model_class_mapping
            model_classes = set(class_mapping.keys())

            missing_in_model = unique_dataset_classes - model_classes
            if missing_in_model:
                logger.warning(f"CRITICAL WARNING: Dataset contains classes not present in the model's mapping: {missing_in_model}!")

            missing_in_dataset = model_classes - unique_dataset_classes
            if missing_in_dataset:
                logger.warning(f"Note: Dataset is missing classes that the model expects: {missing_in_dataset}.")

        elif dataset.mapping_config:
            logger.warning("Model class mapping is missing. Falling back to dataset's mapping_config.")
            class_mapping = dataset.mapping_config
        else:
            unique_classes = sorted(list(unique_dataset_classes))
            class_mapping = {cls_name: idx for idx, cls_name in enumerate(unique_classes)}
            logger.warning(f"No mapping found in Model or Dataset. Dynamically generated mapping for CSV: {class_mapping}")

        try:
            labels = np.array([class_mapping[label] for label in raw_labels])
        except KeyError as e:
            raise ValueError(f"Label {str(e)} from the dataset was not found in the class mapping. Cannot proceed with evaluation.")

        base_dir = os.path.dirname(dataset_path)
        file_paths = [os.path.join(base_dir, str(p)) for p in df[prompt_column].values]

        if len(file_paths) == 0:
            raise ValueError("Failed to find any images in the dataset.")

        def process_path(file_path, label):
            img = tf.io.read_file(file_path)
            img = tf.image.decode_image(img, channels=3, expand_animations=False)
            img = tf.image.resize(img, target_size)
            img = tf.cast(img, tf.float32)

            if preprocess_fn is not None:
                img = preprocess_fn(img)
            else:
                img = tf.keras.applications.xception.preprocess_input(img)

            return img, label

        ds = tf.data.Dataset.from_tensor_slices((file_paths, labels))
        ds = ds.map(process_path, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)

        logger.info("Starting model predictions...")

        y_true_list = []
        y_pred_probs_list = []

        for step, (images_batch, labels_batch) in enumerate(ds, start=1):

            if cancel_check_callback and cancel_check_callback():
                logger.info(f"Cancellation detected at step {step}! Stopping TF predictions.")
                raise TaskCancelledError("Task was cancelled by the user.")

            preds = model.predict(images_batch, verbose=0)
            y_true_list.extend(labels_batch.numpy())
            y_pred_probs_list.extend(preds)

        y_true = np.array(y_true_list)
        y_pred_probs = np.array(y_pred_probs_list)

    total_time_ms = (time.perf_counter() - start_time) * 1000.0

    return models.PredictionResult(
        y_true=y_true,
        y_pred_probs=y_pred_probs,
        processing_time_ms=total_time_ms,
        class_mapping=class_mapping
    )