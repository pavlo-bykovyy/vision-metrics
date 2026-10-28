import csv
import json
from typing import Iterator

from shared import models, enums


def load_prompts_from_dataset(dataset: 'models.Dataset') -> Iterator[dict]:
    """
    Streams data from a dataset file line-by-line based on its format.

    This function acts as a router, delegating the actual file parsing to
    format-specific helper functions (e.g., CSV or JSONL). It extracts
    the necessary schema configuration and ensures the dataset has a valid
    local file artifact before processing to prevent high RAM consumption.

    Args:
        dataset (models.Dataset): The dataset database record. Must contain
            a valid `file_artifact`, `file_format`, `id_column`, and a
            `schema_config` detailing 'input_fields', 'target_fields', and
            'metadata_fields'.

    Yields:
        dict: A dictionary containing the extracted row data:
            - 'original_index' (int): The zero-based row index in the original file.
            - 'row_id' (str | None): The unique identifier from the `id_column`.
            - 'inputs' (dict): Extracted model input fields.
            - 'targets' (dict): Extracted target/label fields.
            - 'metadata' (dict): Extracted metadata fields.

    Raises:
        ValueError: If the dataset lacks an associated file artifact or
            specifies an unsupported file format.
    """
    if not dataset.file_artifact:
        raise ValueError("Dataset does not have an associated local file (Artifact).")

    file_path = dataset.file_artifact.file_path
    schema_config = dataset.schema_config or {}

    input_fields = schema_config.get("input_fields", [])
    target_fields = schema_config.get("target_fields", [])
    metadata_fields = schema_config.get("metadata_fields", [])

    if dataset.file_format == enums.DatasetFormat.CSV:
        yield from _stream_csv(file_path, id_column, input_fields, target_fields, metadata_fields)

    elif dataset.file_format == enums.DatasetFormat.JSONL:
        yield from _stream_jsonl(file_path, id_column, input_fields, target_fields, metadata_fields)

    elif dataset.file_format == enums.DatasetFormat.ARROW:
        yield from _stream_arrow(file_path, id_column, input_fields, target_fields, metadata_fields)

    elif dataset.file_format == enums.DatasetFormat.IMAGE_FOLDER:
        yield from _stream_image_folder(file_path, id_column, input_fields, target_fields, metadata_fields)
    else:
        raise ValueError(f"Unsupported file format: {dataset.file_format}")


def _stream_csv(file_path: str, id_column: str, input_fields: list, target_fields: list, metadata_fields: list) -> Iterator[dict]:
    """
    Parses and streams records from a CSV file line-by-line.

    Args:
        file_path (str): The path to the local CSV file.
        id_column (str): The column name representing the unique row ID.
        input_fields (list): A list of column names mapped to model inputs.
        target_fields (list): A list of column names mapped to target outputs.
        metadata_fields (list): A list of column names mapped to metadata.

    Yields:
        dict: The structured record containing index, id, inputs, targets, and metadata.
              Only yields the record if at least one input field contains a truthy value.

    Raises:
        KeyError: If any of the required schema fields are missing from the CSV headers.
    """
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        all_required_fields = input_fields + target_fields + metadata_fields
        missing_fields = [field for field in all_required_fields if field not in reader.fieldnames]
        if missing_fields:
            raise KeyError(f"Columns {missing_fields} not found in CSV headers.")

        for original_index, row in enumerate(reader):
            row_id = row.get(id_column) if id_column else None

            inputs = {field: row.get(field) for field in input_fields}
            targets = {field: row.get(field) for field in target_fields}
            metadata = {field: row.get(field) for field in metadata_fields}

            if any(inputs.values()):
                yield {
                    "original_index": original_index,
                    "row_id": row_id,
                    "inputs": inputs,
                    "targets": targets,
                    "metadata": metadata
                }


def _stream_jsonl(file_path: str, id_column: str, input_fields: list, target_fields: list, metadata_fields: list) -> Iterator[dict]:
    """
    Parses and streams records from a JSONL (JSON Lines) file line-by-line.

    Args:
        file_path (str): The path to the local JSONL file.
        id_column (str): The key name representing the unique row ID.
        input_fields (list): A list of keys mapped to model inputs.
        target_fields (list): A list of keys mapped to target outputs.
        metadata_fields (list): A list of keys mapped to metadata.

    Yields:
        dict: The structured record containing index, id, inputs, targets, and metadata.
              Only yields the record if at least one input field contains a truthy value.
    """
    with open(file_path, mode='r', encoding='utf-8') as f:
        for original_index, line in enumerate(f):
            if not line.strip():
                continue

            row = json.loads(line)
            row_id = row.get(id_column) if id_column else None

            inputs = {field: row.get(field) for field in input_fields if field in row}
            targets = {field: row.get(field) for field in target_fields if field in row}
            metadata = {field: row.get(field) for field in metadata_fields if field in row}

            if any(inputs.values()):
                yield {
                    "original_index": original_index,
                    "row_id": row_id,
                    "inputs": inputs,
                    "targets": targets,
                    "metadata": metadata
                }

def _stream_arrow(file_path: str, id_column: str, input_fields: list, target_fields: list, metadata_fields: list) -> Iterator[dict]:
    """
    Helper method to parse and stream Apache Arrow (.arrow / .feather) files.
    Reads data in batches to keep memory usage low.
    """
    import pyarrow.ipc as ipc

    with ipc.RecordBatchFileReader(file_path) as reader:
        original_index = 0

        for batch_idx in range(reader.num_record_batches):
            batch = reader.get_batch(batch_idx)
            records = batch.to_pylist()

            for row in records:
                row_id = row.get(id_column) if id_column else None
                inputs = {field: row.get(field) for field in input_fields if field in row}
                targets = {field: row.get(field) for field in target_fields if field in row}
                metadata = {field: row.get(field) for field in metadata_fields if field in row}

                if inputs:
                    yield {
                        "original_index": original_index,
                        "row_id": row_id,
                        "inputs": inputs,
                        "targets": targets,
                        "metadata": metadata
                    }
                original_index += 1


def _stream_image_folder(folder_path: str, id_column: str, input_fields: list, target_fields: list, metadata_fields: list) -> Iterator[dict]:
    """
    Helper method to scan a directory for images.
    Useful for Computer Vision datasets where inputs are file paths.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Path '{folder_path}' is not a valid directory for IMAGE_FOLDER format.")

    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    img_field_name = input_fields[0] if input_fields else "image_path"

    original_index = 0
    for filename in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_extensions:
            full_path = os.path.join(folder_path, filename)

            row_id = filename if id_column == "filename" else str(original_index)

            yield {
                "original_index": original_index,
                "row_id": row_id,
                "inputs": {img_field_name: full_path},
                "targets": {},
                "metadata": {"filename": filename}
            }
            original_index += 1
