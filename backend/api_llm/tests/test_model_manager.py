import pytest

from api_llm.chat.model_manager import DEFAULT_LOAD_PARAMS, ModelManager
from api_llm.schemas.chat import AdapterConfig, AdapterNotFoundError
from shared.enums import ActiveModelStatus

STARTING = ActiveModelStatus.STARTING
READY = ActiveModelStatus.READY
ERROR = ActiveModelStatus.ERROR


class Harness:
    """Fakes for every external dependency of ModelManager."""

    def __init__(self, tmp_path):
        self.tmp_path = tmp_path
        self.configs = {
            1: AdapterConfig("a1.zip", "base-1", {"quantization": "8bit"}),
            2: AdapterConfig("a2.zip", "base-2", None),
        }
        self.statuses = []
        self.load_calls = []
        self.fail_loading = False

    def get_adapter_config(self, adapter_id):
        if adapter_id not in self.configs:
            raise AdapterNotFoundError(f"Adapter {adapter_id} not found")
        return self.configs[adapter_id]

    def set_status(self, adapter_id, status):
        self.statuses.append((adapter_id, status))

    def extract_adapter(self, adapter_path):
        temp_dir = self.tmp_path / adapter_path.removesuffix(".zip")
        temp_dir.mkdir(exist_ok=True)
        return str(temp_dir), str(temp_dir / "model")

    def load_models(self, *, base_model_name, adapter_dir, load_params):
        self.load_calls.append(
            {"base": base_model_name, "dir": adapter_dir, "load_params": load_params}
        )
        if self.fail_loading:
            raise RuntimeError("CUDA out of memory")
        return object(), object(), object()

    def manager(self, **kwargs):
        return ModelManager(
            get_adapter_config=self.get_adapter_config,
            set_status=self.set_status,
            extract_adapter=self.extract_adapter,
            load_models=self.load_models,
            **kwargs,
        )


@pytest.fixture
def harness(tmp_path):
    return Harness(tmp_path)


def test_loads_model_once_per_adapter(harness):
    manager = harness.manager()

    with manager.acquire(1) as first:
        pass
    with manager.acquire(1) as second:
        pass

    assert first is second
    assert len(harness.load_calls) == 1
    assert harness.statuses == [(1, STARTING), (1, READY)]


def test_switching_adapter_replaces_loaded_model(harness):
    manager = harness.manager()

    manager.warm_up(1)
    with manager.acquire(2) as loaded:
        assert loaded.adapter_id == 2

    assert manager.loaded_adapter_id == 2
    assert len(harness.load_calls) == 2


def test_load_failure_sets_error_and_allows_retry(harness):
    manager = harness.manager()
    harness.fail_loading = True

    with pytest.raises(RuntimeError):
        manager.warm_up(1)

    assert manager.loaded_adapter_id is None
    assert harness.statuses[-1] == (1, ERROR)

    harness.fail_loading = False
    manager.warm_up(1)
    assert manager.loaded_adapter_id == 1


def test_failed_switch_does_not_leave_stale_cache(harness):
    """Old bug: after a failed switch the cache still claimed the old adapter."""
    manager = harness.manager()
    manager.warm_up(1)
    harness.fail_loading = True

    with pytest.raises(RuntimeError):
        manager.warm_up(2)

    assert manager.loaded_adapter_id is None


def test_unknown_adapter_reports_error(harness):
    manager = harness.manager()

    with pytest.raises(AdapterNotFoundError):
        manager.warm_up(999)

    assert harness.statuses == [(999, STARTING), (999, ERROR)]


def test_load_params_defaults_and_overrides(harness):
    manager = harness.manager()

    manager.warm_up(2)  # adapter without load_params
    manager.warm_up(1)  # adapter with its own load_params

    assert harness.load_calls[0]["load_params"] == DEFAULT_LOAD_PARAMS
    assert harness.load_calls[1]["load_params"] == {"quantization": "8bit"}


def test_unload(harness):
    manager = harness.manager()
    assert manager.unload() is False

    manager.warm_up(1)
    assert manager.unload() is True
    assert manager.loaded_adapter_id is None


@pytest.mark.parametrize("remove, still_exists", [(False, True), (True, False)])
def test_extracted_files_policy(harness, tmp_path, remove, still_exists):
    manager = harness.manager(remove_extracted_files=remove)

    manager.warm_up(1)
    manager.unload()

    assert (tmp_path / "a1").exists() is still_exists
