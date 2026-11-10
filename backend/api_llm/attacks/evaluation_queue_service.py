"""
evaluation_queue_service.py

This module orchestrates the background processing of model evaluations.
It handles saving tasks to the database queue, dispatching them to Celery,
and managing failure states.
"""

import uuid
from dataclasses import dataclass, field
from celery import chain
from shared.utils.logger import get_logger

from shared import dtos

from api_llm.services.celery_app import celery_app
from api_llm.queues import (
    ATTACK_DATASET_TASK,
    ATTACK_DATASET_QUEUE,
    ATTACK_GENERATION_TASK,
    ATTACK_GENERATION_QUEUE,
    ATTACK_JUDGE_TASK,
    ATTACK_JUDGE_QUEUE,
)

logger = get_logger(__name__)


@dataclass
class AttackDispatch:
    """Celery task IDs generated for an attack run."""
    main_task_id: str
    dataset_task_id: str | None = None
    judge_task_ids: dict[int, str] = field(default_factory=dict)


def trigger_build_attack_dataset(dataset_id: int) -> str:
    """Dispatch an asynchronous Celery task to generate the attack dataset JSONL on the worker."""
    try:
        async_result = celery_app.send_task(
            name=ATTACK_DATASET_TASK,
            queue=ATTACK_DATASET_QUEUE,
            kwargs={"dataset_id": dataset_id},
        )
        logger.info(f"Dispatched attack dataset generation task for dataset_id={dataset_id} (Celery ID: {async_result.id}).")
        return async_result.id
    except Exception as e:
        logger.warning(f"Failed to dispatch attack dataset generation task for dataset_id={dataset_id}: {e}", exc_info=True)
        raise RuntimeError(f"Queue dispatch error: {e}")


def trigger_attack_task(
    evaluation_task_id: int,
    judge_task_run_ids: list[int] | None = None,
    dataset_id: int | None = None,
) -> AttackDispatch:
    """Dispatch an attack run: dataset generation -> model inference -> attack judges in parallel.

    Args:
        evaluation_task_id: DB id of the EvaluationTask.
        judge_task_run_ids: DB ids of JudgeTaskRun records (one per judge).
        dataset_id: Optional DB id of the Dataset to ensure/build on the worker before inference.

    Returns:
        AttackDispatch with generated Celery task IDs.
    """
    from celery import group

    try:
        main_id = str(uuid.uuid4())
        main_task = celery_app.signature(
            ATTACK_GENERATION_TASK,
            kwargs={"evaluation_task_id": evaluation_task_id},
            queue=ATTACK_GENERATION_QUEUE,
            immutable=True,
        ).set(task_id=main_id)

        response = AttackDispatch(main_task_id=main_id)

        steps = []
        if dataset_id is not None:
            ds_task_id = str(uuid.uuid4())
            response.dataset_task_id = ds_task_id
            ds_task = celery_app.signature(
                ATTACK_DATASET_TASK,
                kwargs={"dataset_id": dataset_id},
                queue=ATTACK_DATASET_QUEUE,
                immutable=True,
            ).set(task_id=ds_task_id)
            steps.append(ds_task)

        steps.append(main_task)

        if judge_task_run_ids:
            judge_tasks = []
            for run_id in judge_task_run_ids:
                celery_id = str(uuid.uuid4())
                response.judge_task_ids[run_id] = celery_id
                judge_tasks.append(
                    celery_app.signature(
                        ATTACK_JUDGE_TASK,
                        kwargs={"judge_task_run_id": run_id},
                        queue=ATTACK_JUDGE_QUEUE,
                        immutable=True,
                    ).set(task_id=celery_id)
                )
            steps.append(group(judge_tasks))
            chain(*steps).apply_async()
            logger.info(
                f"Dispatched attack chain (Dataset -> Generation -> {len(judge_task_run_ids)} judges) for task {evaluation_task_id}."
            )
        elif len(steps) > 1:
            chain(*steps).apply_async()
            logger.info(f"Dispatched attack chain (Dataset -> Generation) for task {evaluation_task_id}.")
        else:
            main_task.apply_async()
            logger.info(f"Dispatched attack generation task {evaluation_task_id}.")

        return response

    except Exception as e:
        logger.warning(f"Failed to dispatch attack task: {e}", exc_info=True)
        raise RuntimeError(f"Queue dispatch error: {e}")
