from transformers import AutoTokenizer, AutoModelForCausalLM

from shared import models
from shared.utils.logger import get_logger
from shared.config import MODEL_CACHE_DIR


logger = get_logger(__name__)


def load_judge_base_model(model_name: str, load_params: dict = None) -> tuple:
    """
    Loads a pure base causal language model and its tokenizer for judge evaluation.

    This function initializes the specified base model without any external adapters
    (e.g., LoRA). It also configures the tokenizer, specifically setting the padding
    token and left-padding for correct batched inference. The model is automatically
    set to evaluation mode.

    Args:
        model_name (str): The identifier of the model to load (e.g., a HuggingFace
            repository name or a local directory path).
        load_params (dict, optional): Additional parameters for model loading, such as
            'device_map'. Defaults to None.

    Returns:
        tuple: A 3-element tuple containing:
            - tokenizer (AutoTokenizer): The loaded and configured tokenizer.
            - base_model (AutoModelForCausalLM): The loaded base model in eval mode.
            - model (AutoModelForCausalLM): A reference to the same base model
              (maintained for architectural compatibility).
    """
    if load_params is None:
        load_params = {}

    logger.info(f"Loading tokenizer for judge model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=MODEL_CACHE_DIR)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    logger.info(f"Loading judge base model: {model_name}")

    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        cache_dir=MODEL_CACHE_DIR,
        device_map=load_params.get("device_map", "auto")
    )
    base_model.eval()

    return tokenizer, base_model, base_model