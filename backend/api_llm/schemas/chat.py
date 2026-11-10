"""Plain data containers and errors shared by the chat worker modules."""
from dataclasses import dataclass
from typing import Any, Optional


class ChatRequestNotFoundError(ValueError):
    """Raised when a chat request with the given ID does not exist."""


class AdapterNotFoundError(ValueError):
    """Raised when a LoRA adapter with the given ID does not exist."""


@dataclass(frozen=True)
class ChatJob:
    """Everything the worker needs to answer one chat request."""
    adapter_id: int
    messages: list[dict[str, Any]]
    generation_params: dict[str, Any]


@dataclass(frozen=True)
class AdapterConfig:
    """Everything the worker needs to load one LoRA adapter."""
    adapter_path: str
    base_model_name_or_path: str
    load_params: Optional[dict[str, Any]] = None