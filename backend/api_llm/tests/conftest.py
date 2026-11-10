import os
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# If running in the API container or a lightweight venv without PyTorch installed,
# provide a minimal stub so worker/model modules can be unit-tested without GPU deps.
try:
    import torch  # noqa: F401
except ImportError:
    _fake_torch = types.ModuleType("torch")
    _fake_torch.cuda = MagicMock()
    _fake_torch.cuda.is_available.return_value = False
    sys.modules["torch"] = _fake_torch

# Configure isolated paths and in-memory SQLite before importing application modules
_TEST_TMP_ROOT = Path(tempfile.mkdtemp(prefix="visionmetrics_tests_"))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("UPLOAD_DIR", str(_TEST_TMP_ROOT / "uploaded_models"))
os.environ.setdefault("EXTRACT_BASE_DIR", str(_TEST_TMP_ROOT / "extracted_datasets"))
os.environ.setdefault("MODEL_CACHE_DIR", str(_TEST_TMP_ROOT / "model_cache"))
os.environ.setdefault("ATTACK_DATASETS_DIR", str(_TEST_TMP_ROOT / "uploaded_models" / "attacks"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.database import Base
from shared import models  # noqa: F401 - register ORM models on Base.metadata


@pytest.fixture()
def db_session():
    """Provide a clean, isolated in-memory SQLite SQLAlchemy session per test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
