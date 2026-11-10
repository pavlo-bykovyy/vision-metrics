import gc


def _release_module_tensors(module) -> None:
    """
    Breaks accelerate hook reference cycles and detaches all parameters/buffers
    from a PyTorch module so underlying CUDA storage is freed immediately even if
    an outer frame or exception traceback still references the module object.
    """
    if module is None:
        return

    try:
        from accelerate.hooks import remove_hook_from_submodules
        remove_hook_from_submodules(module)
    except Exception:
        pass

    try:
        if hasattr(module, "cpu"):
            module.cpu()
    except Exception:
        pass

    try:
        for submodule in list(module.modules()):
            if hasattr(submodule, "_parameters"):
                submodule._parameters.clear()
            if hasattr(submodule, "_buffers"):
                submodule._buffers.clear()
        if hasattr(module, "_modules"):
            module._modules.clear()
    except Exception:
        pass


def cleanup_ml_resources(model=None, base_model=None, tokenizer=None) -> None:
    """
    Safely removes machine learning models from GPU memory and forces garbage collection.

    This is a critical step in GPU-bound environments to ensure VRAM is released
    back to the system after an evaluation task completes or fails.
    """
    _release_module_tensors(model)
    if base_model is not None and base_model is not model:
        _release_module_tensors(base_model)

    del model
    del base_model
    del tokenizer

    clear_cuda_cache()


def clear_cuda_cache() -> None:
    """
    Runs Python garbage collection and clears the GPU memory cache + IPC handles.
    """
    gc.collect()

    try:
        import torch
    except ImportError:
        return

    if torch.cuda.is_available():
        try:
            torch.cuda.synchronize()
        except Exception:
            pass
        torch.cuda.empty_cache()
        try:
            torch.cuda.ipc_collect()
        except Exception:
            pass
