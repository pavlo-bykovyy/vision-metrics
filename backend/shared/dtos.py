from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class EvaluationDispatc:
    """
    Response model containing the generated Celery task IDs.
    Used to transfer task tracking IDs from the dispatcher to the database saver.
    """
    main_task_id: str
    judge_task_ids: dict[int, str]