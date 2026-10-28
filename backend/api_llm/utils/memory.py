import gc
import torch


def cleanup_ml_resources(model=None, base_model=None, tokenizer=None) -> None:
    """
    Safely removes machine learning models from memory and forces garbage collection.

    This is a critical step in GPU-bound environments to ensure VRAM is released
    back to the system after an evaluation task completes or fails.

    Args:
        model: The LoRA or specific instantiated model.
        base_model: The underlying foundational LLM.
        tokenizer: The tokenizer associated with the models.
    """
    if model is not None:
        del model
    if base_model is not None:
        del base_model
    if tokenizer is not None:
        del tokenizer

    gc.collect()


def clear_cuda_cache() -> None:
    """
    Clears the graphics card (GPU) memory cache.

    When PyTorch runs AI models, it holds onto video memory (VRAM) just in case
    it needs it again. This function forces PyTorch to return any unused memory
    back to the computer system, which helps prevent "Out Of Memory" crashes.
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
