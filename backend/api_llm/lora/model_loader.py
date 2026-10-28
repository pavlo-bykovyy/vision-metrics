import os
import json
import torch
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from sqlalchemy.orm import Session

from shared import models
from shared.config import MODEL_CACHE_DIR, UPLOAD_DIR
from shared.utils.logger import get_logger
from api_llm.lora.utils import extract_adapter_zip_for_task


logger = get_logger(__name__)


def _sanitize_adapter_config(adapter_dir: str):
    """
    Sanitizes the LoRA adapter configuration file by removing unsupported keys.

    This function reads the `adapter_config.json` file from the specified directory
    and filters its keys against an allowlist. This ensures compatibility with
    older versions of the `peft` library (e.g., v0.11.1) which might crash if
    they encounter unrecognized configuration parameters.

    Args:
        adapter_dir (str): The local directory path containing the `adapter_config.json` file.
    """
    config_path = os.path.join(adapter_dir, "adapter_config.json")
    if not os.path.exists(config_path):
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        supported_keys = {
            "alpha_pattern",
            "auto_mapping",
            "base_model_name_or_path",
            "bias",
            "fan_in_fan_out",
            "inference_mode",
            "init_lora_weights",
            "layers_pattern",
            "layers_to_transform",
            "loftq_config",
            "lora_alpha",
            "lora_dropout",
            "megatron_config",
            "megatron_core",
            "modules_to_save",
            "peft_type",
            "r",
            "rank_pattern",
            "revision",
            "target_modules",
            "task_type",
            "use_dora",
            "use_rslora",
        }

        keys_to_remove = [k for k in config_data.keys() if k not in supported_keys]

        if keys_to_remove:
            for key in keys_to_remove:
                del config_data[key]
                logger.info(
                    f"Removed unknown key '{key}' from adapter_config.json for compatibility."
                )

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)

    except Exception as e:
        logger.warning(f"Failed to sanitize adapter_config.json: {e}")


def _build_quantization_config(quantization: str, model_dtype: torch.dtype) -> Optional[BitsAndBytesConfig]:
    """
    Constructs a BitsAndBytes configuration object for model quantization.

    Depending on the requested quantization level ('4bit' or '8bit'), this helper
    initializes the appropriate settings to load the model efficiently into VRAM.
    For 4-bit quantization, it uses NormalFloat4 (NF4) and double quantization
    for optimal memory saving and performance.

    Args:
        quantization (str): The desired quantization level. Expected values are
            '4bit', '8bit', or 'none'.
        model_dtype (torch.dtype): The PyTorch data type to use for computations
            when applying 4-bit quantization (e.g., torch.float16).

    Returns:
        Optional[BitsAndBytesConfig]: The configured BitsAndBytes object if
        quantization is requested, or None if no valid quantization is specified.
    """
    if quantization == "4bit":
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=model_dtype,
        )
    elif quantization == "8bit":
        return BitsAndBytesConfig(load_in_8bit=True)
    return None


def load_models_from_task(
        task: models.EvaluationTask,
        adapter_dir: str,
        cache_dir: str = MODEL_CACHE_DIR
) -> tuple:
    """
    Safely extracts loading parameters from an EvaluationTask and initializes the model.

    This function acts as a safety wrapper around the core `load_models` function.
    It validates the existence of the task object, ensures a base model name is
    provided, handles potential null values in the database configuration, and
    verifies that the adapter directory exists before delegating the model loading.

    Args:
        task (models.EvaluationTask): The database record containing task
            configurations, including the base model name and loading parameters.
        adapter_dir (str): The local path to the directory containing the
            extracted LoRA adapter.
        cache_dir (str, optional): The directory path for caching Hugging Face
            models. Defaults to MODEL_CACHE_DIR.

    Returns:
        tuple: A tuple containing three elements:
            - tokenizer (AutoTokenizer): The configured tokenizer for the model.
            - base_model (AutoModelForCausalLM): The loaded foundational model.
            - model (PeftModel): The combined model with the LoRA adapter applied.

    Raises:
        ValueError: If the task object is missing or lacks a valid base model name.
        FileNotFoundError: If the specified adapter directory does not exist.
    """
    if not task:
        raise ValueError("The provided task object is None.")

    base_model_name = task.base_model_to_use
    if not base_model_name or not str(base_model_name).strip():
        raise ValueError(f"Task {task.id} has no base_model_to_use specified.")

    load_params = getattr(task, "load_params", {}) or {}

    if not adapter_dir or not os.path.exists(adapter_dir):
        raise FileNotFoundError(f"Adapter directory not found: {adapter_dir}")

    return load_models(
        base_model_name=base_model_name.strip(),
        adapter_dir=adapter_dir,
        load_params=load_params,
        cache_dir=cache_dir
    )


def load_models(
        base_model_name: str,
        adapter_dir: str,
        load_params: dict,
        cache_dir: str = MODEL_CACHE_DIR
) -> tuple:
    """
    Loads a base causal language model, its tokenizer, and applies a specified LoRA adapter.

    This core function dynamically configures model loading based on the provided
    `load_params`. It supports memory-efficient loading techniques such as 4-bit
    and 8-bit quantization (via bitsandbytes), as well as custom PyTorch data types
    (e.g., float16, bfloat16). Finally, it cleans up the model's default generation
    configuration to prevent parameter conflicts during text generation inference.

    Args:
        base_model_name (str): The Hugging Face model identifier or local directory
            path of the foundational model.
        adapter_dir (str): The local directory path containing the extracted LoRA
            adapter weights and configuration file.
        load_params (dict): A dictionary containing model loading configurations.
            Expected keys include 'torch_dtype', 'quantization' ('none', '4bit', '8bit'),
            'device_map', 'trust_remote_code', and 'use_fast_tokenizer'.
        cache_dir (str, optional): The directory path where downloaded models and
            tokenizers are cached. Defaults to MODEL_CACHE_DIR.

    Returns:
        tuple: A tuple containing three elements:
            - tokenizer (AutoTokenizer): The configured tokenizer for the model.
            - base_model (AutoModelForCausalLM): The loaded foundational model.
            - model (PeftModel): The combined model with the LoRA adapter applied,
              ready for inference (eval mode).
    """
    if load_params is None:
        load_params = {}

    def safe_get(key: str, default_val):
        val = load_params.get(key)
        return val if val is not None else default_val

    dtype_mapping = {
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32
    }

    dtype_str = safe_get("torch_dtype", "float16")
    model_dtype = dtype_mapping.get(str(dtype_str).lower(), torch.float16)

    quantization = str(safe_get("quantization", "none")).lower()
    trust_remote_code = bool(safe_get("trust_remote_code", True))
    use_fast_tokenizer = bool(safe_get("use_fast_tokenizer", False))
    device_map = safe_get("device_map", "auto")

    quantization_config = _build_quantization_config(quantization, model_dtype)

    logger.info(f"[1/3] Loading tokenizer for base model: {base_model_name}")
    tokenizer = AutoTokenizer.from_pretrained(
        base_model_name,
        cache_dir=cache_dir,
        use_fast=use_fast_tokenizer,
        trust_remote_code=trust_remote_code,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info(
        f"[2/3] Loading base model '{base_model_name}' (Quantization: {quantization})"
    )

    model_kwargs = {
        "device_map": device_map,
        "cache_dir": cache_dir,
        "trust_remote_code": trust_remote_code,
    }

    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
    else:
        model_kwargs["torch_dtype"] = model_dtype

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name, **model_kwargs
    )

    _sanitize_adapter_config(adapter_dir)

    logger.info(
        f"[3/3] Applying LoRA adapter from: {os.path.basename(adapter_dir)}"
    )
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    try:
        gen_config = getattr(model, "generation_config", None)
        if gen_config is not None:
            gen_config.max_length = None
            for attr in ["temperature", "top_p", "top_k"]:
                if hasattr(gen_config, attr):
                    setattr(gen_config, attr, None)
    except Exception as e:
        logger.warning(f"Failed to reset generation_config: {e}")

    return tokenizer, base_model, model


def load_lora_models(task: models.EvaluationTask, db: Session) -> tuple:
    """
    Handles ZIP extraction, validation, and loading the PEFT model.
    Returns: (tokenizer, base_model, model, temp_extract_dir)
    """
    adapter = db.query(models.LoraAdapter).filter(models.LoraAdapter.id == task.adapter_id).first()
    if not adapter or not os.path.exists(adapter.adapter_path):
        raise FileNotFoundError("Adapter ZIP missing or not found in the database.")

    logger.info(f"Extracting LoRA adapter for task {task.id}")
    temp_extract_dir, actual_model_dir = extract_adapter_zip_for_task(adapter.adapter_path, UPLOAD_DIR)

    tokenizer, base_model, model = load_models(
        base_model_name=task.base_model_to_use,
        adapter_dir=actual_model_dir,
        load_params=task.load_params or {}
    )

    return tokenizer, base_model, model, temp_extract_dir