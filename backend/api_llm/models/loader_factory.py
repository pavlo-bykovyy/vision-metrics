from sqlalchemy.orm import Session
from shared import models, enums
from shared.utils.logger import get_logger

from api_llm.lora.model_loader import load_lora_models
from api_llm.base_model.model_loader import load_base_models


logger = get_logger(__name__)


def load_evaluation_model(task: models.EvaluationTask, db: Session) -> tuple:
    """
    Factory function that determines the task type and delegates
    model loading to the appropriate module.

    Returns: (tokenizer, base_model, model, temp_extract_dir)
    """
    if task.evaluation_type == enums.EvaluationType.LORA:
        logger.info(f"Task {task.id} requires LoRA. Routing to lora.model_loader.")
        return load_lora_models(task, db)

    elif task.evaluation_type == enums.EvaluationType.BASE_MODEL:
        logger.info(f"Task {task.id} requires Base Model. Routing to base_model.model_loader.")
        return load_base_models(task)

    else:
        raise ValueError(f"Unknown evaluation_type: {task.evaluation_type}")