import os
import uuid
import json
import shutil
import zipfile
from typing import Dict, Any


def extract_adapter_config_from_zip(zip_path: str) -> Dict[str, Any]:
    """
    Searches for 'adapter_config.json' inside a ZIP archive without extracting it.
    Reads the file contents into memory and returns the parsed JSON configuration.

    Raises:
        FileNotFoundError: If 'adapter_config.json' is not found within the archive.
        json.JSONDecodeError: If the configuration file contains invalid JSON.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith("adapter_config.json"):
                with zip_ref.open(file_name) as config_file:
                    return json.loads(config_file.read().decode('utf-8'))

    raise FileNotFoundError(f"adapter_config.json not found in {zip_path}")


def extract_adapter_zip_for_task(path: str, base_extract_dir: str) -> tuple[str | None, str]:
    """
    Checks the provided path. If it's a directory, searches for the adapter inside it.
    If it's a ZIP archive, extracts it to a predictable directory (only if not already extracted).

    Args:
        path (str): The path to the adapter's ZIP archive OR an already extracted directory.
        base_extract_dir (str): The root directory where extracted folders will be created.

    Returns:
        tuple: A tuple containing two strings:
            - extract_dir (str | None): The path to the root extracted directory.
            - actual_model_dir (str): The exact path to the directory containing 'adapter_config.json'.

    Raises:
        FileNotFoundError: If the provided path doesn't exist or 'adapter_config.json' is missing.
        ValueError: If the file is not a valid ZIP archive.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Adapter path not found: {path}")

    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            if "adapter_config.json" in files:
                return None, root
        raise FileNotFoundError(f"adapter_config.json not found in directory: {path}")

    filename = os.path.basename(path)
    folder_name = f"extracted_{filename.replace('.zip', '')}"
    extract_dir = os.path.join(base_extract_dir, folder_name)

    if os.path.exists(extract_dir):
        for root, dirs, files in os.walk(extract_dir):
            if "adapter_config.json" in files:
                return extract_dir, root

        shutil.rmtree(extract_dir, ignore_errors=True)

    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(extract_dir, ignore_errors=True)
        raise ValueError(f"File is not a valid ZIP archive: {path}")

    for root, dirs, files in os.walk(extract_dir):
        if "adapter_config.json" in files:
            return extract_dir, root

    shutil.rmtree(extract_dir, ignore_errors=True)
    raise FileNotFoundError(f"adapter_config.json not found inside extracted zip: {path}")
