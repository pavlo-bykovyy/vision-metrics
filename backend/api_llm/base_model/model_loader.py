from transformers import AutoTokenizer, AutoModelForCausalLM
from shared import models
from shared.utils.logger import get_logger
from shared.config import MODEL_CACHE_DIR


logger = get_logger(__name__)


def load_base_models(task: models.EvaluationTask) -> tuple:
    """
    Loads a pure base model without any LoRA adapters.
    Returns: (tokenizer, base_model, model, temp_extract_dir)
    Note: model and base_model are identical here, temp_extract_dir is None.
    """
    base_model_name = task.base_model_to_use
    load_params = task.load_params or {}

    logger.info(f"Loading tokenizer for base model: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, cache_dir=MODEL_CACHE_DIR)

    logger.info(f"Loading base model: {base_model_name}")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        cache_dir=MODEL_CACHE_DIR,
        device_map=load_params.get("device_map", "auto")
    )
    base_model.eval()

    return tokenizer, base_model, base_model, None