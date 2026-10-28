"""
evaluation_queue_service.py

This module orchestrates the background processing of model evaluations.
It handles saving tasks to the database queue, dispatching them to Celery,
and managing failure states.
"""

import uuid
from celery import chain
from shared.utils.logger import get_logger
from api_llm.services.celery_app import celery_app

from shared import dtos


logger = get_logger(__name__)


def trigger_evaluation_task(evaluation_task_id: int, judge_task_run_ids: list[int] = None) -> dtos.EvaluationDispatc:
    """
    Dispatches the evaluation task to the Celery queue for background processing.
    Generates and sets specific Celery task IDs for all tasks in the workflow
    to allow tracking in the database.

    Args:
        evaluation_task_id (int): The database ID of the evaluation.
        judge_task_run_ids (list[int], optional): A list of database IDs for the judge tasks.
                                                  Defaults to None.

    Returns:
        EvaluationDispatchResponse: A Pydantic model containing the generated Celery task IDs.
    """
    try:
        main_celery_task_id = str(uuid.uuid4())

        main_task = celery_app.signature(
            "llm.evaluation",
            kwargs={"evaluation_task_id": evaluation_task_id},
            queue="llm_tasks",
            immutable=True
        ).set(task_id=main_celery_task_id)

        response = dtos.EvaluationDispatc(
            main_task_id=main_celery_task_id,
            judge_task_ids={}
        )

        if judge_task_run_ids:
            judge_tasks = []

            for judge_id in judge_task_run_ids:
                judge_celery_task_id = str(uuid.uuid4())
                response.judge_task_ids[judge_id] = judge_celery_task_id

                judge_task = celery_app.signature(
                    "llm.judge_evaluation",
                    kwargs={"judge_task_run_id": judge_id},
                    queue="llm_tasks",
                    immutable=True
                ).set(task_id=judge_celery_task_id)

                judge_tasks.append(judge_task)

            workflow = chain(main_task, group(judge_tasks))
            workflow.apply_async()

            logger.info(f"Successfully dispatched chained task (Generation -> {len(judge_task_run_ids)} Judges) for task {evaluation_task_id}.")
        else:
            main_task.apply_async()
            logger.info(f"Successfully dispatched task {evaluation_task_id} to Celery.")

        return response

    except Exception as e:
        logger.warning(f"Failed to dispatch Celery task: {e}", exc_info=True)
        raise RuntimeError(f"Queue dispatch error: {e}")
