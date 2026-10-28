import os

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploaded_models")

os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTRACT_BASE_DIR = os.getenv("EXTRACT_BASE_DIR", "/app/extracted_datasets")

os.makedirs(EXTRACT_BASE_DIR, exist_ok=True)

EVAL_BATCH_SIZE = int(os.getenv("EVAL_BATCH_SIZE") or "32")

DB_FLUSH_BATCH = int(os.getenv("DB_FLUSH_BATCH") or "32")

JUDGE_BATCH_SIZE = int(os.getenv("JUDGE_BATCH_SIZE") or "32")

MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/app/model_cache")
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)