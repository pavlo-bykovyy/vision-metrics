import os
from itertools import islice
from typing import Iterable, Iterator, Any
from sqlalchemy.orm import Session

from shared import models, enums
from shared.database import SessionLocal
from shared.datasets.dataset_readers import load_prompts_from_dataset
from shared.utils.logger import get_logger


logger = get_logger(__name__)


def prepare_prompts(task: 'models.EvaluationTask', db: 'Session') -> Iterator[dict]:
    """
    Prepares a continuous stream of prompts for the model to process.

    This function checks the task settings. If a dataset ID is provided, it retrieves
    the data from the corresponding file. If there is no dataset but a single
    prompt is given, it will just use that one prompt. We use a generator (Iterator)
    here because it helps save computer memory when reading very large files.

    Args:
        task (models.EvaluationTask): The task object containing settings like
            the dataset ID or a single prompt text.
        db (Session): The active database connection used to find the dataset.

    Returns:
        Iterator[dict]: A memory-efficient generator that provides dictionaries
        one by one. Each dictionary contains:
            - 'prompt_id' (str): The unique row ID or line number.
            - 'inputs' (dict): The dictionary of input fields from the dataset.
            - 'input_text' (str): A stringified version of the prompt/inputs.

    Raises:
        ValueError: If the dataset cannot be found, has no file, or if the task
            is completely empty.
        FileNotFoundError: If the database says a file exists, but it is missing
            from the computer's hard drive.
    """
    template = getattr(task, 'prompt_template', None)

    def _format_text_for_model(inputs_dict: dict, prompt_template: str | None) -> str:
        if prompt_template and prompt_template.strip() not in ["{input_text}", "{prompt}"]:
            try:
                return prompt_template.format(**inputs_dict)
            except KeyError as e:
                logger.warning(f"Template KeyError: Missing column {e} in dataset. Falling back to default format.")

        if len(inputs_dict) == 1:
            return str(list(inputs_dict.values())[0])

        return "\n\n".join(f"{k.capitalize()}: {v}" for k, v in inputs_dict.items() if v is not None)

    if task.dataset_id:
        dataset = db.query(models.Dataset).filter(models.Dataset.id == task.dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {task.dataset_id} not found.")

        if not dataset.file_artifact:
            raise ValueError(f"Dataset {task.dataset_id} has no associated file artifact.")

        file_path = dataset.file_artifact.file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file missing: {file_path}")

        logger.info(f"[Task {task.id}] Loading dataset from {file_path}")

        prompts_to_process = (
            {
                "prompt_id": str(item["row_id"]) if item.get("row_id") is not None else f"row_{item['original_index']}",
                "inputs": item["inputs"],
                "targets": item.get("targets", {}),
                "metadata": item.get("metadata", {}),
                "input_text": _format_text_for_model(item["inputs"], template)
            }
            for item in load_prompts_from_dataset(dataset)
        )

    elif getattr(task, 'prompt', None):
        logger.info(f"[Task {task.id}] No dataset provided. Using single task.prompt")

        raw_prompt = str(task.prompt)
        formatted_prompt = _format_text_for_model({"prompt": raw_prompt}, template) if template else raw_prompt

        prompts_to_process = iter([{
            "prompt_id": f"single_prompt_{task.id}",
            "inputs": {"prompt": raw_prompt},
            "targets": {},
            "metadata": {},
            "input_text": formatted_prompt
        }])
    else:
        raise ValueError("No dataset_id and no prompt provided for this task.")

    return prompts_to_process


def chunk_iterable(iterable: Iterable[Any], size: int) -> Iterator[list[Any]]:
    """
    Breaks a large collection of items into smaller groups (batches).

    When working with AI models, we often can't process all data at once because
    it would use up too much computer memory. This function helps by giving us
    manageable pieces of data one at a time.

    Args:
        iterable (Iterable[Any]): The large list or generator of items you want to split.
        size (int): The maximum number of items you want in each smaller group.

    Yields:
        Iterator[list[Any]]: A generator that produces lists (batches) of the
        requested size. The last batch might be smaller if there aren't enough items left.
    """
    iterator = iter(iterable)
    for first in iterator:
        yield [first] + list(islice(iterator, size - 1))


def save_batch_to_db(db: Session, records: list[models.EvaluationResult]) -> bool:
    """
    Saves a group of evaluation results to the database all at once.

    Saving items in a batch (bulk save) is much faster than saving them one by one.
    If something goes wrong during the save process, this function will cancel
    the operation (rollback) so your database doesn't get corrupted with partial data.

    Args:
        db (Session): The active database connection.
        records (list[models.EvaluationResult]): A list of results that need to be saved.

    Returns:
        bool: Returns True if the save was successful. Returns False if an error
        happened or if there was nothing to save.
    """
    if not records:
        return False

    try:
        db.bulk_save_objects(records)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.warning(f"Failed to bulk save evaluation results to DB: {e}")
        return False


def update_status_to_failed(evaluation_task_id: int, error_msg: str):
    """
    Updates the status of a specific evaluation record to 'FAILED' and saves the error message.

    This helper function is called when an exception occurs during the
    evaluation process inside the worker.

    Args:
        evaluation_task_id (int): The unique identifier of the evaluation record.
        error_msg (str): The description or representation of the error.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        eval_record = db.query(models.EvaluationTask).filter(models.EvaluationTask.id == evaluation_task_id).first()

        if eval_record:
            eval_record.status = enums.TaskStatus.FAILED
            eval_record.error_message = str(error_msg)[:255]
            db.commit()
            logger.info(f"Status updated to FAILED for evaluation_task_id: {evaluation_task_id}")
        else:
            logger.warning(f"Warning: Evaluation record {evaluation_task_id} NOT FOUND. Cannot update to FAILED.")

    except Exception as db_err:
        db.rollback()
        logger.warning(f"Failed to update status to failed in database: {db_err}")
    finally:
        db.close()
