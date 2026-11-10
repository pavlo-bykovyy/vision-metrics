from transformers import AutoTokenizer, AutoModelForCausalLM
from shared import models
from shared.utils.logger import get_logger
from shared.config import MODEL_CACHE_DIR
from api_llm.lora.model_loader import build_model_load_kwargs


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
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_name,
        cache_dir=MODEL_CACHE_DIR,
        trust_remote_code=bool(load_params.get("trust_remote_code", True)),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info(f"Loading base model: {base_model_name}")
    model_kwargs = build_model_load_kwargs(load_params=load_params, cache_dir=MODEL_CACHE_DIR)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        **model_kwargs,
    )
    base_model.eval()

    return tokenizer, base_model, base_model, None