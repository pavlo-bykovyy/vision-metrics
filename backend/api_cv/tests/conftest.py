import os
import tempfile
from pathlib import Path

# Isolated paths and in-memory SQLite before any `shared.*` import (shared.config creates dirs on import).
_TEST_TMP_ROOT = Path(tempfile.mkdtemp(prefix="visionmetrics_cv_tests_"))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("UPLOAD_DIR", str(_TEST_TMP_ROOT / "uploaded_models"))
os.environ.setdefault("EXTRACT_BASE_DIR", str(_TEST_TMP_ROOT / "extracted_datasets"))
os.environ.setdefault("MODEL_CACHE_DIR", str(_TEST_TMP_ROOT / "model_cache"))
