import os
import time
import zipfile
import shutil
import uuid
import numpy as np
import tensorflow as tf

from shared.utils.logger import get_logger
from shared import models
from shared.config import EVAL_BATCH_SIZE, EXTRACT_BASE_DIR
from contextlib import contextmanager


logger = get_logger(__name__)


@contextmanager
def extract_and_cleanup_zip(dataset_path: str, extract_base_dir: str):
    """
    Extracts a ZIP archive to a unique temporary directory and ensures its safe removal after use.

    This context manager generates a unique directory name, extracts the contents of the
    specified ZIP file, and yields the path to the extracted directory. It guarantees that
    the directory and its contents are deleted upon exiting the context, regardless of exceptions.

    Args:
        dataset_path (str): The absolute file path to the ZIP archive.
        extract_base_dir (str): The base directory where the temporary folder will be created.

    Yields:
        str: The path to the temporary directory containing the extracted files.
    """
    base_name = os.path.basename(dataset_path).replace('.zip', '')
    unique_suffix = uuid.uuid4().hex[:8]
    extract_dir = os.path.join(extract_base_dir, f"{base_name}_{unique_suffix}")

    if not os.path.exists(extract_dir):
        logger.info(f"Extracting ZIP archive to {extract_dir} for faster processing...")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    else:
        logger.info(f"Using already extracted dataset at {extract_dir}...")

    try:
        yield extract_dir
    finally:
        if os.path.exists(extract_dir):
            logger.info(f"Cleaning up: Deleting extracted directory {extract_dir}")
            try:
                shutil.rmtree(extract_dir)
                logger.info("Cleanup successful.")
            except Exception as e:
                logger.warning(f"Failed to delete extracted directory {extract_dir}: {e}")

def resolve_class_mapping(evaluation, dataset):
    """
    Determines the appropriate class mapping to use for evaluation.

    This function prioritizes the class mapping defined directly in the model.
    If not available, it falls back to the dataset's mapping configuration.

    Args:
        evaluation: The evaluation configuration object containing model metadata.
        dataset: The dataset object containing fallback mapping configurations.

    Returns:
        dict | None: The resolved class mapping dictionary, or None if neither source provides one.
    """
    if evaluation.model.class_mapping:
        logger.info(f"Using class mapping from the Model: {evaluation.model.class_mapping}")
        return evaluation.model.class_mapping

    if dataset.mapping_config:
        logger.warning(f"Model mapping missing. Falling back to Dataset's mapping_config: {dataset.mapping_config}")
        return dataset.mapping_config

    return None

def scan_dataset_directory(extract_dir: str, class_mapping: dict):
    """
    Scans the extracted dataset directory, filters valid image files, and assigns labels.

    This function traverses the directory structure, filtering out system files and unsupported
    formats. It skips folders that are not present in the provided class mapping. If no mapping
    is provided, it dynamically generates one based on the discovered subdirectories.

    Args:
        extract_dir (str): The root directory containing the extracted dataset.
        class_mapping (dict): A dictionary mapping class names to integer labels. Can be None.

    Returns:
        tuple: A tuple containing:
            - valid_files (list): A list of absolute file paths to valid images.
            - all_y_true (list): A list of corresponding integer labels for the images.
            - class_mapping (dict): The final class mapping dictionary used.

    Raises:
        ValueError: If no valid image files are found after filtering.
    """
    valid_files = []
    raw_labels = []

    logger.info("Scanning extracted folder for valid images...")
    for root, _, files in os.walk(extract_dir):
        class_name = os.path.basename(root)

        if class_mapping and str(class_name) not in class_mapping:
            if root != extract_dir:
                logger.warning(f"Skipping entire folder '{class_name}': not in database classes.")
            continue

        for file_name in files:
            if file_name.startswith('._') or '__MACOSX' in root:
                continue
            if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                continue

            raw_labels.append(class_name)
            valid_files.append(os.path.join(root, file_name))

    if not valid_files:
        raise ValueError("No valid images were found after class validation.")

    if class_mapping:
        unique_dataset_classes = set(raw_labels)
        model_classes = set(class_mapping.keys())
        missing_in_dataset = model_classes - unique_dataset_classes
        if missing_in_dataset:
            logger.warning(f"Note: Dataset is missing classes that the mapping expects: {missing_in_dataset}.")
    else:
        unique_classes = sorted(list(set(raw_labels)))
        class_mapping = {str(cls_name): idx for idx, cls_name in enumerate(unique_classes)}
        logger.warning(f"No mapping found in DB at all. Dynamically generated: {class_mapping}")

    all_y_true = [class_mapping[str(label)] for label in raw_labels]

    return valid_files, all_y_true, class_mapping


def create_tf_pipeline(valid_files: list, target_size: tuple, batch_size: int, fallback_size: int = 256):
    """
    Constructs an optimized TensorFlow data pipeline for image loading and preprocessing.

    This function safely determines the target image dimensions. If the provided target_size
    contains None (e.g., for models accepting variable input sizes), it uses a fallback dimension.
    It then creates a tf.data.Dataset, decodes images, resizes them, applies preprocessing,
    and configures optimal batching and prefetching.

    Args:
        valid_files (list): A list of file paths to the images.
        target_size (tuple): The target dimensions (height, width) for image resizing.
        batch_size (int): The number of images per batch.
        fallback_size (int, optional): The default dimension to use if target_size contains None. Defaults to 256.

    Returns:
        tf.data.Dataset: The configured TensorFlow dataset ready for inference.
    """
    target_height = int(target_size[0]) if target_size and target_size[0] is not None else fallback_size
    target_width = int(target_size[1]) if target_size and target_size[1] is not None else fallback_size
    tf_target_size = [target_height, target_width]

    def load_and_preprocess_image(file_path):
        img = tf.io.read_file(file_path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img = tf.image.resize(img, tf_target_size)
        img = tf.keras.applications.xception.preprocess_input(img)
        return img

    path_ds = tf.data.Dataset.from_tensor_slices(valid_files)
    image_ds = path_ds.map(load_and_preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
    image_ds = image_ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return image_ds


def process_zip_in_batches(evaluation,
                           target_size: tuple,
                           model,
                           batch_size: int = EVAL_BATCH_SIZE):
    """
    Orchestrates the evaluation pipeline by extracting a ZIP dataset, processing images in batches,
    and generating model predictions.

    This function serves as the main coordinator for the evaluation workflow. It utilizes a context
    manager to safely extract and clean up the dataset archive. It then resolves the appropriate
    class mapping, scans the directory for valid images, constructs an optimized TensorFlow data
    pipeline, and performs batch inference using the provided model.

    Args:
        evaluation: The evaluation configuration object containing dataset and model metadata.
        target_size (tuple): The target dimensions (height, width) to which input images will be resized.
        model: The loaded machine learning model used to generate predictions.
        batch_size (int, optional): The number of images to process in each batch. Defaults to 32.

    Returns:
        models.PredictionResult: An object encapsulating the true labels, predicted probabilities,
        total processing time in milliseconds, and the final class mapping used during evaluation.
    """
    dataset = evaluation.dataset
    start_time = time.perf_counter()
    dataset_path = dataset.file_artifact.file_path

    with extract_and_cleanup_zip(dataset_path, EXTRACT_BASE_DIR) as extract_dir:
        initial_mapping = resolve_class_mapping(evaluation, dataset)
        valid_files, all_y_true, final_mapping = scan_dataset_directory(extract_dir, initial_mapping)

        logger.info(f"Found {len(valid_files)} valid images. Starting tf.data.Dataset pipeline...")

        image_ds = create_tf_pipeline(valid_files, target_size, batch_size)
        all_y_pred_probs = model.predict(image_ds)

    total_time_ms = (time.perf_counter() - start_time) * 1000.0

    return models.PredictionResult(
        y_true=np.array(all_y_true),
        y_pred_probs=np.array(all_y_pred_probs),
        processing_time_ms=total_time_ms,
        class_mapping=final_mapping
    )
