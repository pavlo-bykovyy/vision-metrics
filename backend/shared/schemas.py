from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from fastapi import Form
import json

from shared import enums


class ModelBasic(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class DatasetBasic(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class ArtifactResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MetricBase(BaseModel):
    """
    Pydantic schema for evaluation metrics.
    Includes basic metrics, imbalanced dataset metrics, calibration, and operational data.
    """
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None

    mcc: Optional[float] = None
    balanced_accuracy: Optional[float] = None
    pr_auc: Optional[float] = None

    log_loss_value: Optional[float] = None
    brier_score: Optional[float] = None

    mean_latency_ms: Optional[float] = None
    model_size_bytes: Optional[int] = None

    averaging_mode: Optional[str] = None
    decision_threshold: Optional[float] = None

    tp: Optional[int] = 0
    fp: Optional[int] = 0
    tn: Optional[int] = 0
    fn: Optional[int] = 0

    class_mapping: Optional[dict] = None

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Evaluation(BaseModel):
    """
    Base schema for an Evaluation record.
    Used for endpoints that trigger or create an evaluation without
    needing to load the associated metrics immediately.
    """
    id: int
    model_id: int
    dataset_id: Optional[int] = None
    status: str
    error_message: Optional[str] = Field(default=None, validation_alias="error_message")
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
class EvaluationDetail(BaseModel):
    id: int
    model_id: int
    dataset_id: Optional[int] = None
    status: str
    error_message: Optional[str] = Field(default=None, validation_alias="error_message")
    created_at: Optional[datetime] = None
    metrics: Optional[MetricBase] = None

    model: Optional[ModelBasic] = None
    dataset: Optional[DatasetBasic] = None

    model_config = ConfigDict(from_attributes=True)

class EvaluationPaginationResponse(BaseModel):
    items: list[EvaluationDetail]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)

class ModelCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    arch_id: int
    weights_id: int
    class_mapping: Optional[dict] = None

class ModelDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    arch_file_id: Optional[int] = None
    weights_file_id: Optional[int] = None
    class_mapping: Optional[dict] = None
    evaluations: list[EvaluationDetail] = []

    model_config = ConfigDict(from_attributes=True)

class ModelPaginationResponse(BaseModel):
    items: list[ModelDetail]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)

class EvaluateModelRequest(BaseModel):
    dataset_id: int
    model_id: int

class StorageInfo(BaseModel):
    total: float
    used: float
    free: float
    percentage: int
    unit: str

    model_config = ConfigDict(from_attributes=True)

class EvaluateRequest(BaseModel):
    """
    Data model for the evaluation request payload.
    Used by the API endpoint to validate incoming data before creating an EvaluationTask.
    """
    adapter_id: Optional[int] = None
    base_model_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    dataset_id: Optional[int] = None
    generation_params: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {
            "max_new_tokens": 256,
            "temperature": 0.1,
            "top_k": 40,
            "top_p": 0.9,
            "repetition_penalty": 1.15,
            "system_prompt": None
        }
    )
    judge_ids: Optional[list[int]] = []

class LoraAdapterResponse(BaseModel):
    id: int
    task_type: Optional[str] = None
    base_model_name_or_path: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class LoraAdapterListResponse(BaseModel):
    adapters: list[LoraAdapterResponse]

    model_config = ConfigDict(from_attributes=True)

class DatasetCreateForm:
    """
    Form dependency class to handle multipart/form-data metadata during dataset upload.
    This keeps the router signature clean while parsing form fields correctly.
    """
    def __init__(
            self,
            name: str = Form(...),
            dataset_type: enums.DatasetType = Form(enums.DatasetType.NONE),
            file_source: enums.DatasetSource = Form(enums.DatasetSource.LOCAL_FILE),
            file_format: enums.DatasetFormat = Form(enums.DatasetFormat.NONE),
            source_url: Optional[str] = Form(None),
            id_column: Optional[str] = Form(None),
            schema_config: Optional[str] = Form(None),
            class_mapping: Optional[str] = Form(None),
    ):
        self.name = name
        self.dataset_type = dataset_type
        self.file_source = file_source
        self.file_format = file_format
        self.source_url = source_url
        self.id_column = id_column

        self.schema_config: dict[str, Any] = {}
        if schema_config:
            try:
                self.schema_config = json.loads(schema_config)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='Invalid JSON format for schema_config. Ensure you are using double quotes, for example: {"input_fields": ["question"], "target_fields": ["answer"]}'
                )

        self.mapping_config: dict[str, Any] = {}
        if class_mapping:
            try:
                self.mapping_config = json.loads(class_mapping)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail='Invalid JSON format for class mapping. Ensure you are using double quotes, for example: {"cats": 0, "dogs": 1}'
                )

class DatasetDetail(BaseModel):
    id: int
    name: str
    source_url: Optional[str] = None
    artifact_id: Optional[int] = None
    dataset_type: Optional[enums.DatasetType] = None
    file_source: Optional[enums.DatasetSource] = None
    file_format: Optional[enums.DatasetFormat] = None
    id_column: Optional[str] = None
    schema_config: Optional[dict[str, Any]] = None
    mapping_config: Optional[dict] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DatasetUpdateRequest(BaseModel):
    name: Optional[str] = None
    dataset_type: Optional[enums.DatasetType] = None
    file_source: Optional[enums.DatasetSource] = None
    file_format: Optional[enums.DatasetFormat] = None
    id_column: Optional[str] = None
    schema_config: Optional[dict[str, Any]] = None
    class_mapping: Optional[dict] = None

class ModelUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LoraEvaluationMetricResponse(BaseModel):
    """
    Schema for serializing aggregated LLM evaluation metrics.
    """
    id: int
    task_id: int
    schema_validity_rate: Optional[float] = None
    mean_tps: Optional[float] = None
    mean_vram_mb: Optional[float] = None
    mean_latency_sec: Optional[float] = None
    mean_logprob: Optional[float] = None
    total_samples: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class EvaluationTaskResponse(BaseModel):
    """
    Schema for a single LoRA evaluation task response.
    """
    id: int
    adapter_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = Field(default=None, validation_alias="error_message")
    created_at: Optional[datetime] = None
    metrics: Optional[LoraEvaluationMetricResponse] = None
    adapter: Optional["LoraAdapterResponse"] = None
    judge_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class EvaluationTaskListResponse(BaseModel):
    """
    Schema for a list of evaluation tasks.
    """
    tasks: list[EvaluationTaskResponse]

    model_config = ConfigDict(from_attributes=True)

class EvaluationResultResponse(BaseModel):
    """
    Schema for a single generated output from an EvaluationTask.
    """
    id: int
    task_id: int
    prompt_id: Optional[str] = None
    input_text: str
    generated_text: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_seconds: Optional[float] = None
    peak_memory_mb: Optional[float] = None
    avg_logprob: Optional[float] = None

    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EvaluationResultPaginationResponse(BaseModel):
    """
    Schema for a paginated list of evaluation results.
    Aligns with the standard pagination format used across the API.
    """
    items: list[EvaluationResultResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class JudgeBase(BaseModel):
    model_name: str
    name: Optional[str] = None
    description: Optional[str] = None


class JudgeResponse(JudgeBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JudgePaginationResponse(BaseModel):
    """
    Schema for a paginated list of judges.
    """
    items: list[JudgeResponse]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)


class ActiveModelStartRequest(BaseModel):
    """
    Payload required to register and start a new active model worker.
    """
    adapter_id: int

class ActiveModelResponse(BaseModel):
    """
    Response schema detailing the current state and queue of an active model.
    """
    id: int
    adapter_id: Optional[int] = None
    queue_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class ActiveModelStatusUpdateRequest(BaseModel):
    """
    Payload for manually updating the status of an active model.
    """
    status: enums.ActiveModelStatus

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    generation_params: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {
            "max_new_tokens": 256,
            "temperature": 0.1,
            "top_k": 40,
            "top_p": 0.9,
            "repetition_penalty": 1.15,
            "system_prompt": None
        }
    )

class ChatResponse(BaseModel):
    answer: str
    model: str

class SimpleModelInfo(BaseModel):
    id: str
    name: str

class ModelsListResponse(BaseModel):
    data: list[SimpleModelInfo]

class JudgeRunCreate(BaseModel):
    """
    Schema for creating a new Judge Task Run.
    Used for validating incoming data from the client.
    """
    evaluation_task_id: int = Field(
        ...,
        description="ID of the base evaluation task to be judged."
    )
    judge_id: int = Field(
        ...,
        description="ID of the judge model that will perform the evaluation."
    )
    name: Optional[str] = Field(
        default=None,
        description="Optional custom name for this specific execution run."
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description or notes regarding this run."
    )
    judge_params: dict[str, Any] = Field(
        ...,
        description="Dictionary containing specific parameters for the judge model (e.g., temperature, max_tokens)."
    )

class JudgeTaskRunResponse(BaseModel):
    id: int
    evaluation_task_id: Optional[int] = None
    judge_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: enums.TaskStatus = enums.TaskStatus.NONE
    result: Optional[str] = None
    error_message: Optional[str] = Field(default=None, validation_alias="error_message")
    judge_params: Optional[dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JudgeTaskRunPaginationResponse(BaseModel):
    items: list[JudgeTaskRunResponse]
    total: int
    page: int
    size: int
    pages: int

