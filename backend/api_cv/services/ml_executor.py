"""
ml_executor.py

This file handles all heavy machine learning computations, including
loading TensorFlow/Keras models and calculating metrics.
"""

from tensorflow import keras
from shared import models
from shared.utils.logger import get_logger
from shared.config import EVAL_BATCH_SIZE
from api_cv.services.metrics_calculator import calculate_metrics
from api_cv.services.dataset_processor import get_predictions
from api_cv.services.model_loader import load_keras_model


logger = get_logger(__name__)


def load_and_evaluate_model(evaluation: models.Evaluation,
                            cancel_check_callback=None) -> dict:
    """
    Orchestrates the loading of a Keras model, processes the dataset, and calculates evaluation metrics.

    This function acts as a pipeline that delegates the model instantiation to the loader module,
    extracts required input/output shapes, performs batch predictions, and finally computes
    performance metrics.

    Args:
        evaluation (models.Evaluation): The database evaluation record containing references to
            the model (architecture, weights, class mapping) and the dataset to be evaluated.
        cancel_check_callback (callable, optional): A function returning a boolean to check
            if the task has been cancelled by the user.

    Returns:
        dict: A dictionary containing the raw calculated evaluation metrics.
    """
    logger.info("Step 2: Loading the ML model...")

    evaluation_model = evaluation.model
    weights_path = evaluation_model.weights.file_path

    model = load_keras_model(
        arch_path=evaluation_model.architecture.file_path,
        weights_path=weights_path,
    )

    if model is None:
        raise RuntimeError("Failed to load model")

    output_shape = model.output_shape
    last_dim = output_shape[-1]

    input_shape = model.input_shape
    if isinstance(input_shape, list):
        input_shape = input_shape[0]
    target_size = input_shape[1:3]

    logger.debug(f"Model successfully loaded. Target size: {target_size}")

    logger.info("Step 3a: Getting model predictions (optimized)...")
    prediction_result = get_predictions(
        evaluation=evaluation,
        model=model,
        target_size=target_size,
        batch_size=EVAL_BATCH_SIZE,
        cancel_check_callback=cancel_check_callback
    )

    logger.info("Step 3b: Calculating metrics...")

    raw_metrics = calculate_metrics(
        prediction_result=prediction_result,
        last_dim=last_dim,
        weights_path=weights_path,
    )

    return raw_metrics