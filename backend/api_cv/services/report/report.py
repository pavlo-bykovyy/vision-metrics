from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from shared.models import Evaluation
from api_cv.services.report.diagnostics import MetricProfile, build_report
from api_cv.services.report.renderers import to_html, to_markdown


def load(db: Session, evaluation_id: int) -> tuple[dict[str, Any], MetricProfile]:
    ev = Evaluation.get_by_id(db, evaluation_id)
    if ev is None:
        raise HTTPException(404, f"Evaluation {evaluation_id} not found")
    if ev.metrics is None:
        status = getattr(ev.status, "value", ev.status)
        raise HTTPException(409, f"Evaluation {evaluation_id} has no metrics yet (status={status})")
    if (ev.metrics.averaging_mode or "binary") != "binary":
        raise HTTPException(422, "Diagnostic report supports binary evaluations only")

    meta = {
        "evaluation_id": ev.id,
        "model_id": ev.model_id,
        "model_name": ev.model.name if ev.model else None,
        "dataset_id": ev.dataset_id,
        "dataset_name": ev.dataset.name if ev.dataset else None,
        "created_at": ev.created_at.isoformat() if ev.created_at else None,
        "class_mapping": ev.metrics.class_mapping or (ev.model.class_mapping if ev.model else None),
    }
    return meta, MetricProfile.from_metric(ev.metrics)