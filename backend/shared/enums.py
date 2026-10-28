import enum

class TaskStatus(str, enum.Enum):
    NONE = "none"
    PENDING = "pending"
    DOWNLOADING = "downloading"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    CANCELLED = "canceled"
    FAILED = "failed"

class JudgeStatus(str, enum.Enum):
    NONE = "none"
    PENDING = "pending"
    JUDGING = "judging"
    COMPLETED = "completed"
    CANCELLED = "canceled"
    FAILED = "failed"

class ActiveModelStatus(str, enum.Enum):
    """
    Defines the lifecycle states of an active model worker.
    """
    NONE = "none"
    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    ERROR = "error"
    STOPPED = "stopped"

class DatasetType(str, enum.Enum):
    NONE = "none"
    CV = "cv"
    LLM = "llm"

class DatasetFormat(str, enum.Enum):
    NONE = "none"
    CSV = "csv"
    JSONL = "jsonl"
    IMAGE_FOLDER = "image_folder"
    ARROW = "arrow"

class DatasetSource(str, enum.Enum):
    NONE = "none"
    LOCAL_FILE = "local_file"
    DIRECT_URL = "direct_url"
    KAGGLE = "kaggle"
    HUGGING_FACE = "hugging_face"

class EvaluationType(enum.Enum):
    NONE = "none"
    BASE_MODEL = "base_model"
    LORA = "lora"
