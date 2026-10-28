import json
from sqlalchemy.orm import Session
from shared import models


def calculate_multicriteria_profile(db: Session, task_id: int) -> str:
    """
    Computes a multi-criteria profile vector (q) for a completed evaluation task.

    This function retrieves all generated evaluation results associated with a
    specific task and aggregates both operational efficiency metrics (latency,
    throughput, VRAM usage) and predictive quality indicators (schema validity).

    Args:
        db (Session): The active SQLAlchemy database session.
        task_id (int): The unique identifier of the evaluation task.

    Returns:
        str: A JSON-formatted string representing the multi-criteria profile,
             or an error message if no results are found.
    """
    results = db.query(models.EvaluationResult).filter(models.EvaluationResult.task_id == task_id).all()

    if not results:
        raise ValueError("No results found for scoring.")

    total_tps = 0.0
    total_vram = 0.0
    total_latency = 0.0
    total_logprob = 0.0
    valid_schema_count = 0

    n = len(results)

    for res in results:
        latency = res.latency_seconds or 0.001
        tokens = res.completion_tokens or 0

        tps = tokens / latency
        total_tps += tps
        total_vram += (res.peak_memory_mb or 0)
        total_latency += latency
        total_logprob += (res.avg_logprob or 0.0)

        try:
            json.loads(res.generated_text)
            valid_schema_count += 1
        except json.JSONDecodeError:
            pass

    metric_record = models.LoraEvaluationMetric(
        task_id=task_id,
        schema_validity_rate=round(valid_schema_count / n, 4),
        mean_tps=round(total_tps / n, 2),
        mean_vram_mb=round(total_vram / n, 2),
        mean_latency_sec=round(total_latency / n, 2),
        mean_logprob=round(total_logprob / n, 4),
        total_samples=n
    )

    return metric_record