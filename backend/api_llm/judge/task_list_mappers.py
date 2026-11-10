"""
Mappers that convert ORM models into the universal ``TaskListItem`` schema.

This module is the single place where model-specific fields are translated
into the shape expected by the frontend tasks table. Supporting a new task type
only requires adding one more ``*_to_item`` function here.
"""
import json
import logging
from typing import Any, Callable, Optional

from sqlalchemy.orm import Query

from shared import schemas, enums

logger = logging.getLogger(__name__)

_STATUS_ALIASES = {
    "pending": "pending",
    "queued": "pending",
    "created": "pending",
    "none": "pending",
    "running": "running",
    "processing": "running",
    "in_progress": "running",
    "started": "running",
    "completed": "completed",
    "done": "completed",
    "success": "completed",
    "succeeded": "completed",
    "finished": "completed",
    "failed": "failed",
    "error": "failed",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "revoked": "cancelled",
}


def normalize_status(raw: Any) -> str:
    """
    Converts a raw status value into one of the universal UI statuses.

    Unknown values are logged and treated as ``pending``.

    Args:
        raw (Any): An Enum member, a string, or None.

    Returns:
        str: One of ``pending``, ``running``, ``completed``, ``failed``, ``cancelled``.
    """
    value = getattr(raw, "value", raw)
    key = str(value if value is not None else "none").strip().lower()
    state = _STATUS_ALIASES.get(key)
    if state is None:
        logger.warning("Unknown task status %r, falling back to 'pending'", raw)
        return "pending"
    return state


def _as_text(value: Any) -> Optional[str]:
    """
    Converts an arbitrary result value into a string suitable for the UI.

    Args:
        value (Any): A string, a number, a JSON-serializable object, or None.

    Returns:
        Optional[str]: The string representation, or None if the value is None.
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except TypeError:
        return str(value)


def evaluation_task_to_item(task) -> schemas.TaskListItem:
    """
    Maps an ``EvaluationTask`` ORM object to a ``TaskListItem``.

    Args:
        task (models.EvaluationTask): The evaluation task to convert.

    Returns:
        schemas.TaskListItem: The universal row representation.
    """
    category = getattr(task, "task_category", None)
    kind = "attack" if category == enums.TaskCategory.ATTACK else "evaluation"
    return schemas.TaskListItem(
        id=task.id,
        kind=kind,
        name=task.name or f"Evaluation #{task.id}",
        description=task.description,
        status=normalize_status(task.status),
        result=_as_text(task.result),
        error_message=task.error_message,
        created_at=task.created_at,
    )


def judge_run_to_item(run) -> schemas.TaskListItem:
    """
    Maps a ``JudgeTaskRun`` ORM object to a ``TaskListItem``.

    The name falls back to the related evaluation task name and then to a
    generated label. The description falls back to a reference to the evaluation
    task and the judge the run belongs to, so the row is never blank.

    Args:
        run (models.JudgeTaskRun): The judge run to convert.

    Returns:
        schemas.TaskListItem: The universal row representation.
    """
    parent = getattr(run, "evaluation_task", None)
    parent_name = getattr(parent, "name", None)

    return schemas.TaskListItem(
        id=run.id,
        kind="judge",
        name=run.name or parent_name or f"Judge run #{run.id}",
        description=run.description or f"Evaluation task #{run.evaluation_task_id} · Judge #{run.judge_id}",
        status=normalize_status(run.status),
        result=_as_text(run.result),
        error_message=run.error_message,
        created_at=run.created_at,
    )


def build_task_list(
        query: Query,
        mapper: Callable[[Any], schemas.TaskListItem],
        size: int = 100,
) -> schemas.TaskListResponse:
    """
    Builds a universal task list response from any SQLAlchemy query.

    Args:
        query (Query): A query that already has its ordering and eager loading applied.
        mapper (Callable): A function converting one ORM row into a ``TaskListItem``.
        size (int): The maximum number of rows to return. Defaults to 100.

    Returns:
        schemas.TaskListResponse: The converted rows together with the total count.
    """
    total = query.count()
    rows = query.limit(size).all()
    return schemas.TaskListResponse(items=[mapper(row) for row in rows], total=total)
