"""
Owns the LoRA model that is currently loaded in this worker process.

The manager knows nothing about Celery or the database: everything external
(adapter lookup, status reporting, unzip, model loading) is injected, which
keeps the load/switch/unload logic unit-testable.
"""
import gc
import shutil
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Optional, Protocol, Tuple

from api_llm.schemas.chat import AdapterConfig
from shared.enums import ActiveModelStatus

from shared.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_LOAD_PARAMS: dict[str, Any] = {
    "torch_dtype": "bfloat16",
    "quantization": "4bit",
    "device_map": "auto",
    "use_fast_tokenizer": False,
}


class ModelLoader(Protocol):
    def __call__(
        self, *, base_model_name: str, adapter_dir: str, load_params: dict[str, Any]
    ) -> Tuple[Any, Any, Any]:
        """Returns (tokenizer, base_model, model)."""


# adapter_path -> (temp_extract_dir, actual_model_dir)
AdapterExtractor = Callable[[str], Tuple[str, str]]


@dataclass(frozen=True)
class LoadedModel:
    adapter_id: int
    tokenizer: Any
    base_model: Any
    model: Any
    temp_extract_dir: Optional[str] = None


def _free_gpu_memory(model=None, base_model=None, tokenizer=None) -> None:
    from api_llm.utils.memory import cleanup_ml_resources, clear_cuda_cache

    cleanup_ml_resources(model, base_model, tokenizer)
    clear_cuda_cache()


def _remove_dir(path: Optional[str]) -> None:
    if path:
        shutil.rmtree(path, ignore_errors=True)


class ModelManager:
    """
    Keeps at most one model loaded and swaps it when another adapter is requested.

    Invariant: `_loaded` is either None or a fully loaded model. A failed load
    or switch can never leave a stale or half-deleted cache behind.
    """

    def __init__(
        self,
        *,
        get_adapter_config: Callable[[int], AdapterConfig],
        set_status: Callable[[int, ActiveModelStatus], None],
        extract_adapter: AdapterExtractor,
        load_models: ModelLoader,
        remove_extracted_files: bool = False,
    ) -> None:
        self._get_adapter_config = get_adapter_config
        self._set_status = set_status
        self._extract_adapter = extract_adapter
        self._load_models = load_models
        # Extracted adapter files stay on disk by default (matches old behaviour).
        self._remove_extracted_files = remove_extracted_files

        # RLock: callers hold it for a whole generation, loading re-enters it.
        self._lock = threading.RLock()
        self._loaded: Optional[LoadedModel] = None

    @property
    def loaded_adapter_id(self) -> Optional[int]:
        loaded = self._loaded
        return loaded.adapter_id if loaded else None

    @contextmanager
    def acquire(self, adapter_id: int) -> Iterator[LoadedModel]:
        """
        Yields the model for `adapter_id`, loading it first if needed.

        The lock is held for the whole `with` block, so an unload or a switch
        in another thread can't free the model while it is being used.
        """
        with self._lock:
            yield self._ensure_loaded(adapter_id)

    def warm_up(self, adapter_id: int) -> None:
        with self.acquire(adapter_id):
            pass

    def unload(self) -> bool:
        """Frees the model and VRAM. Returns False if nothing was loaded."""
        with self._lock:
            return self._release()

    def _ensure_loaded(self, adapter_id: int) -> LoadedModel:
        loaded = self._loaded
        if loaded is not None and loaded.adapter_id == adapter_id:
            return loaded
        return self._load(adapter_id)

    def _load(self, adapter_id: int) -> LoadedModel:
        logger.info(f"Worker is initializing model: {adapter_id}")
        self._set_status(adapter_id, ActiveModelStatus.STARTING)

        self._release()

        try:
            loaded = self._build(adapter_id)
        except Exception:
            logger.exception(f"Failed to load model {adapter_id}")
            _free_gpu_memory()
            self._set_status(adapter_id, ActiveModelStatus.ERROR)
            raise

        self._loaded = loaded
        self._set_status(adapter_id, ActiveModelStatus.READY)
        return loaded

    def _build(self, adapter_id: int) -> LoadedModel:
        config = self._get_adapter_config(adapter_id)
        temp_dir, model_dir = self._extract_adapter(config.adapter_path)

        try:
            tokenizer, base_model, model = self._load_models(
                base_model_name=config.base_model_name_or_path,
                adapter_dir=model_dir,
                load_params=dict(config.load_params or DEFAULT_LOAD_PARAMS),
            )
        except Exception:
            self._cleanup_files(temp_dir)
            raise

        return LoadedModel(
            adapter_id=adapter_id,
            tokenizer=tokenizer,
            base_model=base_model,
            model=model,
            temp_extract_dir=temp_dir,
        )

    def _release(self) -> bool:
        loaded, self._loaded = self._loaded, None
        if loaded is None:
            return False

        temp_dir = loaded.temp_extract_dir
        logger.info(f"Releasing model: {loaded.adapter_id}")
        _free_gpu_memory(loaded.model, loaded.base_model, loaded.tokenizer)
        del loaded  # drop the last references before collecting

        _free_gpu_memory()
        self._cleanup_files(temp_dir)
        return True

    def _cleanup_files(self, temp_dir: Optional[str]) -> None:
        if self._remove_extracted_files:
            _remove_dir(temp_dir)