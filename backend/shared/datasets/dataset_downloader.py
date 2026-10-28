import os
import requests
import zipfile
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from shared import models, enums
from shared.config import UPLOAD_DIR


def download_dataset_if_needed(db: Session, task: models.EvaluationTask) -> None:
    """
    Downloads a dataset from an external source if it has not been downloaded yet.

    Depending on the dataset's source (Kaggle, Hugging Face, or a direct URL),
    this function retrieves the data, extracts it if it is a ZIP archive,
    cleans up the raw archive, and registers the local path as an Artifact
    in the database.

    Args:
        db (Session): The active SQLAlchemy database session.
        task (models.EvaluationTask): The evaluation task containing the target dataset_id.

    Raises:
        ValueError: If the dataset is not found, lacks a source URL, or uses an unsupported source.
        RuntimeError: If a database transaction fails during the artifact registration.
        requests.exceptions.RequestException: If the direct HTTP download fails.
    """
    if not task.dataset_id:
        return

    dataset = db.query(models.Dataset).filter(models.Dataset.id == task.dataset_id).first()
    if not dataset:
        raise ValueError(f"Dataset with ID {task.dataset_id} not found in DB.")

    if dataset.file_artifact and os.path.exists(dataset.file_artifact.file_path):
        return

    if dataset.file_source in [enums.DatasetSource.LOCAL_FILE, enums.DatasetSource.NONE]:
        return

    if not dataset.source_url:
        raise ValueError(f"Dataset {dataset.name} requires a download but has no source_url.")

    base_storage_dir = UPLOAD_DIR
    os.makedirs(base_storage_dir, exist_ok=True)
    local_path = None

    if dataset.file_source == enums.DatasetSource.KAGGLE:
        import kagglehub
        local_path = kagglehub.dataset_download(dataset.source_url)

    elif dataset.file_source == enums.DatasetSource.HUGGING_FACE:
        from huggingface_hub import snapshot_download
        local_path = snapshot_download(
            repo_id=dataset.source_url,
            repo_type="dataset",
            local_dir=os.path.join(base_storage_dir, dataset.name)
        )

    elif dataset.file_source == enums.DatasetSource.DIRECT_URL:
        file_name = os.path.basename(urlparse(dataset.source_url).path) or f"{dataset.id}_file.dat"
        raw_download_path = os.path.join(base_storage_dir, f"{dataset.id}_{file_name}")

        response = requests.get(dataset.source_url, stream=True)
        response.raise_for_status()

        with open(raw_download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if raw_download_path.lower().endswith('.zip'):
            extract_dir = os.path.join(base_storage_dir, f"{dataset.id}_extracted_{file_name[:-4]}")
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(raw_download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            os.remove(raw_download_path)

            local_path = extract_dir
        else:
            local_path = raw_download_path

    else:
        raise ValueError(f"Unsupported download source: {dataset.file_source}")

    try:
        new_artifact = models.Artifact(file_path=local_path)
        db.add(new_artifact)
        db.commit()
        db.refresh(new_artifact)

        dataset.artifact_id = new_artifact.id
        db.commit()
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Database error during artifact registration: {e}")