"""
Database Schema for ML & LLM Evaluation Platform.

This module defines the SQLAlchemy ORM models for managing two distinct workflows:
1. Classical ML Pipeline: Tracking traditional models, weights, and statistical metrics.
2. Generative AI Pipeline: Managing LoRA adapters, evaluation tasks, and text generation results.
"""

from dataclasses import dataclass

from typing import Optional
import numpy as np
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text, Enum as SQLEnum, JSON, Table
from sqlalchemy.orm import relationship, joinedload, Session
from sqlalchemy.sql import func
import math

from shared.database import Base
from shared.enums import (
    TaskStatus,
    DatasetFormat,
    ActiveModelStatus,
    JudgeStatus,
    EvaluationType,
    TaskCategory,
    DatasetType,
    DatasetSource
)


class Artifact(Base):
    """
    Stores metadata and physical file paths for uploaded assets.

    This includes files like model weights (.h5, .pt) or JSON architectures
    used to reconstruct models in the worker environment.
    """
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Dataset(Base):
    """
    Universal registry for datasets used across the platform.

    Both classical ML models and LLMs reference this table to know which
    data to use for evaluation.
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    source_url = Column(String, nullable=True)

    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=True)

    file_artifact = relationship("Artifact", foreign_keys=[artifact_id])

    dataset_type = Column(SQLEnum(DatasetType, name="dataset_type_enum"), default=DatasetType.NONE)
    file_format = Column(SQLEnum(DatasetFormat, name="dataset_format_enum"), default=DatasetFormat.NONE)
    file_source = Column(SQLEnum(DatasetSource, name="dataset_source_enum"), default=DatasetSource.NONE)

    id_column = Column(String, nullable=True)

    schema_config = Column(JSON, default={}, nullable=True)

    mapping_config = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    evaluations = relationship("Evaluation", back_populates="dataset", cascade="all, delete-orphan")
    evaluation_tasks = relationship("EvaluationTask", back_populates="dataset", cascade="all, delete-orphan")


# ---------------------------------------------------------
# Classical ML Models (Testing metrics like Accuracy, F1)
# ---------------------------------------------------------

class Model(Base):
    """
    Represents a classical ML model composed of uploaded artifacts.

    A model must have both an architecture file and a weights file to be
    loaded and evaluated by the worker.
    """
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign keys linking to physical files
    arch_file_id = Column(Integer, ForeignKey("artifacts.id"), index=True)
    weights_file_id = Column(Integer, ForeignKey("artifacts.id"), index=True)

    architecture = relationship("Artifact", foreign_keys=[arch_file_id])
    weights = relationship("Artifact", foreign_keys=[weights_file_id])

    class_mapping = Column(JSON, nullable=True)

    evaluations = relationship("Evaluation", back_populates="model", cascade="all, delete-orphan")

    @classmethod
    def get_by_id(cls, db: Session, model_id: int):
        """
        Retrieves a single ML model by its ID.

        Args:
            db (Session): The active database session.
            model_id (int): The unique identifier of the model to find.

        Returns:
            Model | None: The model object if found, otherwise None.
        """
        return db.query(cls).filter(cls.id == model_id).first()

    @property
    def metrics(self):
        """
        Convenience property to fetch the metrics from the most recent evaluation run.
        Returns None if the model has not been evaluated yet.
        """
        if self.evaluations:
            return self.evaluations[-1].metrics
        return None


class Evaluation(Base):
    """
    Records a specific execution instance of a classical ML Model evaluated against a Dataset.

    A single model can have multiple evaluations over time (e.g., tested against
    different datasets or re-tested after code changes).
    """
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)

    celery_task_id = Column(String, nullable=True)

    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), index=True)

    status = Column(SQLEnum(TaskStatus, name="task_status_enum"), default=TaskStatus.PENDING)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    model = relationship("Model", back_populates="evaluations")
    dataset = relationship("Dataset", back_populates="evaluations")
    metrics = relationship("Metric", back_populates="evaluation", uselist=False, cascade="all, delete-orphan")

    @classmethod
    def get_paginated(cls, db: Session, page: int, size: int):
        """
        Retrieves a paginated list of evaluations along with their preloaded metrics.

        Args:
            db (Session): The active database session.
            page (int): The current page number (1-indexed).
            size (int): The maximum number of items to return per page.

        Returns:
            tuple: A tuple containing three elements:
                - items (list): The list of evaluation objects for the requested page.
                - total_count (int): The total number of evaluations in the database.
                - pages (int): The total calculated number of pages.
        """
        # Calculate the number of records to skip based on the current page
        offset = (page - 1) * size
        total_count = db.query(cls).count()

        # Fetch the items, eagerly loading metrics and ordering from newest to oldest
        items = db.query(cls) \
            .options(joinedload(cls.metrics)) \
            .order_by(cls.id.desc()) \
            .offset(offset) \
            .limit(size) \
            .all()

        # Calculate total pages, ensuring at least 1 page is returned even if empty
        pages = math.ceil(total_count / size) if total_count > 0 else 1

        return items, total_count, pages

    @classmethod
    def get_by_id(cls, db: Session, evaluation_id: int):
        """
        Retrieves a single evaluation record by its ID, including its associated metrics.

        Args:
            db (Session): The active database session.
            evaluation_id (int): The unique identifier of the evaluation to find.

        Returns:
            Evaluation | None: The evaluation object if found, otherwise None.
        """
        return db.query(cls) \
            .options(
            joinedload(cls.metrics),
            joinedload(cls.model),
            joinedload(cls.dataset)
        ) \
            .filter(cls.id == evaluation_id) \
            .first()

    @classmethod
    def update_status(cls, db_session, evaluation_id: int, new_status: TaskStatus, error_message: str = None):
        """
        Class method to safely update the status of an evaluation.

        Args:
            db_session: The SQLAlchemy database session.
            evaluation_id (int): The ID of the evaluation to update.
            new_status (TaskStatus): The new status to apply.
            error_message (str, optional): An error message if the status is FAILED.
        """
        eval_record = db_session.query(cls).filter(cls.id == evaluation_id).first()

        if not eval_record:
            raise ValueError(f"Evaluation record {evaluation_id} not found in the database.")

        eval_record.status = new_status
        if error_message:
            eval_record.error_message = str(error_message)[:255]

        db_session.commit()
        return eval_record

    @classmethod
    def delete_by_id(cls, db: Session, evaluation_id: int) -> bool:
        """
        Deletes a specific evaluation from the database by its ID.

        Args:
            db (Session): The active database session.
            evaluation_id (int): The unique identifier of the evaluation to delete.

        Returns:
            bool: True if the record was successfully found and deleted,
                  False if the record did not exist.
        """
        db_eval = cls.get_by_id(db, evaluation_id)

        # If the evaluation doesn't exist, exit early and return False
        if not db_eval:
            return False

        db.delete(db_eval)
        db.commit()


class Metric(Base):
    """
    Stores the statistical metrics resulting from a classical Model Evaluation.
    """
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), unique=True, index=True)

    # Core performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)

    mcc = Column(Float, nullable=True)
    balanced_accuracy = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)

    log_loss_value = Column(Float, nullable=True)
    brier_score = Column(Float, nullable=True)

    mean_latency_ms = Column(Float, nullable=True)
    model_size_bytes = Column(Integer, nullable=True)

    averaging_mode = Column(String, default="binary") # 'binary', 'macro', 'weighted'
    decision_threshold = Column(Float, default=0.5)

    # Confusion matrix metrics.
    # These are nullable because absolute counts (True Positives, etc.)
    # may not directly apply or make sense in multi-class scenarios.
    tp = Column(Integer, nullable=True)
    fp = Column(Integer, nullable=True)
    tn = Column(Integer, nullable=True)
    fn = Column(Integer, nullable=True)

    class_mapping = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    evaluation = relationship("Evaluation", back_populates="metrics")


@dataclass
class PredictionResult:
    """
    Data class representing the output of the model prediction phase.

    Attributes:
        y_true (np.ndarray): Array of true labels from the dataset.
        y_pred_probs (np.ndarray): Array of probabilities predicted by the model.
        processing_time_ms (float): Total time spent on data loading and prediction.
    """
    y_true: np.ndarray
    y_pred_probs: np.ndarray
    processing_time_ms: float
    class_mapping: Optional[dict] = None


# ---------------------------------------------------------
# LLM & LoRA Adapters (Text Generation Testing)
# ---------------------------------------------------------

class LoraAdapter(Base):
    """
    Registers fine-tuned Low-Rank Adaptation (LoRA) modules for LLMs.
    """
    __tablename__ = "lora_adapters"

    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String, unique=True, index=True, nullable=False)
    adapter_path = Column(String, nullable=False)
    task_type = Column(String, nullable=True)

    # The foundational LLM required to load this specific adapter
    base_model_name_or_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    evaluation_tasks = relationship("EvaluationTask", back_populates="adapter", cascade="all, delete-orphan")


class EvaluationTask(Base):
    """
    Represents a queued or completed text-generation job for a LoRA adapter.

    Can be used to process an entire dataset or run a single ad-hoc prompt.
    """
    __tablename__ = "evaluation_tasks"

    id = Column(Integer, primary_key=True, index=True)

    celery_task_id = Column(String, nullable=True)

    evaluation_type = Column(SQLEnum(EvaluationType, name="evaluation_type_enum"), default=EvaluationType.NONE)
    task_category = Column(
        SQLEnum(TaskCategory, name="task_category_enum"),
        default=TaskCategory.NONE,
        nullable=False,
        index=True,
    )

    adapter_id = Column(Integer, ForeignKey("lora_adapters.id"), nullable=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True, index=True)

    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus, name="task_status_enum"), default=TaskStatus.NONE)

    # Generation parameters passed to the LLM inference engine
    base_model_to_use = Column(Text, nullable=True)
    prompt = Column(Text, nullable=True) # Used if testing a single prompt instead of a full dataset

    load_params = Column(JSON, default={
        "torch_dtype": "float16",
        "quantization": "4bit",
        "device_map": "auto",
        "trust_remote_code": True,
        "use_fast_tokenizer": False
    })

    generation_params = Column(JSON, default={
        "max_new_tokens": 256,
        "temperature": 0.1,
        "top_k": 40,
        "top_p": 0.9,
        "repetition_penalty": 1.15,
        "system_prompt": None
    })

    prompt_template = Column(Text, default="{input_text}", nullable=True)

    # Top-level execution logs
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    judge_status = Column(SQLEnum(JudgeStatus, name="judge_status_enum"), default=JudgeStatus.NONE)
    judge_ids = Column(JSON, nullable=True, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    adapter = relationship("LoraAdapter", back_populates="evaluation_tasks")
    dataset = relationship("Dataset", back_populates="evaluation_tasks")
    results = relationship("EvaluationResult", back_populates="task", cascade="all, delete-orphan")

    metrics = relationship("LoraEvaluationMetric", back_populates="task", uselist=False, cascade="all, delete-orphan")
    judge_runs = relationship("JudgeTaskRun", back_populates="evaluation_task", cascade="all, delete-orphan")
    attack_visualization_runs = relationship(
        "AttackVisualizationRun",
        secondary="attack_visualization_run_tasks",
        back_populates="evaluation_tasks",
    )
    attack_charts = relationship(
        "AttackChart",
        secondary="attack_chart_tasks",
        back_populates="evaluation_tasks",
    )


class EvaluationResult(Base):
    """
    Stores the actual generated text outputs produced by an EvaluationTask,
    along with operational and probability metrics.

    If an EvaluationTask processes a dataset with 1,000 rows, this table
    will contain 1,000 corresponding records linking the input prompt to the generated response.
    """
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("evaluation_tasks.id"), index=True)

    prompt_id = Column(String, nullable=True)

    input_text = Column(Text, nullable=False)
    generated_text = Column(Text, nullable=False)

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    latency_seconds = Column(Float, nullable=True)
    peak_memory_mb = Column(Float, nullable=True)

    avg_logprob = Column(Float, nullable=True)

    metadata_ = Column("metadata", JSON, default={}, nullable=True)

    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("EvaluationTask", back_populates="results")

    judge_evaluations = relationship("JudgeEvaluation", back_populates="result", cascade="all, delete-orphan")


class LoraEvaluationMetric(Base):
    """
    Strict relational storage for aggregated LLM evaluation metrics.
    """
    __tablename__ = "lora_evaluation_metrics"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("evaluation_tasks.id"), unique=True, index=True)

    schema_validity_rate = Column(Float, nullable=True)

    mean_tps = Column(Float, nullable=True)
    mean_vram_mb = Column(Float, nullable=True)
    mean_latency_sec = Column(Float, nullable=True)

    mean_logprob = Column(Float, nullable=True)

    total_samples = Column(Integer, nullable=True)

    task = relationship("EvaluationTask", back_populates="metrics")


class JudgeTaskRun(Base):
    """
    Represents an asynchronous background task (Celery task) for an LLM-as-a-Judge.
    Links the base generation task (EvaluationTask) with a specific judge (Judge),
    allowing for independent tracking of evaluation status, errors, and generation parameters.
    """
    __tablename__ = "judge_task_runs"

    id = Column(Integer, primary_key=True, index=True)

    evaluation_task_id = Column(Integer, ForeignKey("evaluation_tasks.id", ondelete="CASCADE"), index=True)
    judge_id = Column(Integer, ForeignKey("judges.id", ondelete="CASCADE"), index=True)

    celery_task_id = Column(String, nullable=True)

    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(TaskStatus, name="task_status_enum"), default=TaskStatus.NONE)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    judge_params = Column(JSON, default={
        "temperature": 0.0,
        "max_new_tokens": 512,
        "system_prompt": None
    })

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    evaluation_task = relationship("EvaluationTask", back_populates="judge_runs")
    judge = relationship("Judge", back_populates="judge_runs")

    evaluations = relationship("JudgeEvaluation", back_populates="judge_task_run", cascade="all, delete-orphan")
    attack_charts = relationship(
        "AttackChart",
        secondary="attack_chart_judge_runs",
        back_populates="judge_task_runs",
    )


class Judge(Base):
    """
    Registry for LLMs used as automated judges in the evaluation pipeline.
    """
    __tablename__ = "judges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    model_name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    judge_runs = relationship("JudgeTaskRun", back_populates="judge", cascade="all, delete-orphan")


class JudgeEvaluation(Base):
    """
    Stores the evaluation scores and reasoning provided by an LLM-as-a-Judge
    for a specific generated text.
    """
    __tablename__ = "judge_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("evaluation_results.id"), index=True)

    judge_model_id = Column(Integer, ForeignKey("judges.id"), index=True)

    judge_task_run_id = Column(Integer, ForeignKey("judge_task_runs.id"), nullable=True, index=True)

    safety_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    hallucination_score = Column(Float, nullable=True)

    metric_category = Column(String, nullable=True)

    reasoning = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    judge = relationship("Judge")
    result = relationship("EvaluationResult", back_populates="judge_evaluations")
    judge_task_run = relationship("JudgeTaskRun", back_populates="evaluations")


class ActiveModel(Base):
    """
    Database representation of a currently active model instance.
    Tracks the assigned Celery queue and current operational status.
    """
    __tablename__ = "active_models"

    id = Column(Integer, primary_key=True, index=True)
    adapter_id = Column(Integer, ForeignKey("lora_adapters.id"), unique=True, nullable=True)
    base_model_id = Column(String, nullable=True)
    queue_name = Column(String, unique=True, nullable=False)

    load_params = Column(JSON, default={
        "torch_dtype": "float16",
        "quantization": "4bit",
        "device_map": "auto",
        "trust_remote_code": True,
        "use_fast_tokenizer": False
    })

    status = Column(
        SQLEnum(ActiveModelStatus, name="active_model_status_enum"),
        default=ActiveModelStatus.NONE
    )

    adapter = relationship("LoraAdapter")


class ChatRequestRecord(Base):
    """
    Table for storing incoming chat requests.

    This model captures the configuration parameters (like temperature and max_tokens)
    and the message history sent by the user or external system to the LLM.
    """
    __tablename__ = "chat_requests"

    id = Column(Integer, primary_key=True, index=True)
    adapter_id = Column(Integer, ForeignKey("lora_adapters.id"), index=True, nullable=True)
    model_name = Column(String, nullable=False)
    generation_params = Column(JSON, default={
        "max_new_tokens": 256,
        "temperature": 0.1,
        "top_k": 40,
        "top_p": 0.9,
        "repetition_penalty": 1.15,
        "system_prompt": None
    })

    messages = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    response = relationship("ChatResponseRecord", back_populates="request", uselist=False)

    adapter = relationship("LoraAdapter")


class ChatResponseRecord(Base):
    """
    Table for storing generated responses from the model.

    This model holds the final text generated by the LLM and links
    directly back to the original request that triggered it.
    """
    __tablename__ = "chat_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("chat_requests.id"), unique=True, nullable=True)

    answer = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    request = relationship("ChatRequestRecord", back_populates="response")


# ---------------------------------------------------------
# Dynamic Attack & Scenario Templates (replaces hardcoded notebook dicts)
# ---------------------------------------------------------

class AttackTaskConfig(Base):
    """
    Stores dynamic task-level specifications and INFERENCE_PROMPTS (SYSTEM/USER templates,
    task_instruction, baseline ground truths, prefixes, and default sample entities)
    for tasks like 'heroes', 'disinfo', or custom user tasks.
    """
    __tablename__ = "attack_task_configs"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(80), unique=True, index=True, nullable=False)
    expected_output_format = Column(String(50), default="free_text", nullable=False)
    max_new_tokens = Column(Integer, default=180, nullable=False)

    # Mapping of language (e.g. 'ENGLISH', 'UKRAINIAN', 'RUSSIAN') ->
    # {
    #   "task_instruction": "...",
    #   "baseline_gt": "...",
    #   "baseline_gt_real": "...",
    #   "baseline_gt_fake": "...",
    #   "title_prefix": "TITLE",
    #   "body_prefix": "ARTICLE",
    #   "system": "...",
    #   "user": "..."
    # }
    languages_config = Column(JSON, default=dict, nullable=False)

    # Optional default sample entities (e.g. hero names list or {"real": [...], "fake": [...]})
    default_entities = Column(JSON, default=dict, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AttackTemplate(Base):
    """
    Stores editable scenario and attack categories (e.g. 'baseline', 'baseline_real',
    'baseline_fake', 'safety_attack', 'stereotyping', 'cultural_bias', 'toxicity',
    'hallucination', 'extraction') per task, along with per-language prompt templates
    and expert ground-truth expectations.
    """
    __tablename__ = "attack_templates"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(80), index=True, nullable=False, default="heroes")
    key = Column(String(80), index=True, nullable=False)
    metric_category = Column(String(80), index=True, nullable=False)
    variant = Column(String(40), nullable=True)

    goal = Column(Text, nullable=False, default="Evaluate model compliance and safety.")
    check_canary = Column(Boolean, default=False, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Mapping of language -> attack/scenario instruction text (e.g. {"UKRAINIAN": "...", "ENGLISH": "..."})
    text = Column(JSON, default=dict, nullable=False)

    # Mapping of language -> expert_ground_truth (from gt_map in notebook)
    ground_truth = Column(JSON, default=dict, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AttackTechnique(Base):
    """
    Stores editable prompt-wrapping techniques (e.g. 'direct', 'ignore',
    'persona', 'roleplay', 'base64') with per-language templates containing
    '{t}' or '{b64_t}'.
    """
    __tablename__ = "attack_techniques"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(80), unique=True, index=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Mapping of language -> wrapper template (e.g. {"UKRAINIAN": "... {t}", "ENGLISH": "... {t}"})
    templates = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ---------------------------------------------------------
# Attack Visualization & Chart Persistence (M2M with Tasks & Judge Runs)
# ---------------------------------------------------------

attack_visualization_run_tasks = Table(
    "attack_visualization_run_tasks",
    Base.metadata,
    Column(
        "visualization_run_id",
        Integer,
        ForeignKey("attack_visualization_runs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "evaluation_task_id",
        Integer,
        ForeignKey("evaluation_tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

attack_chart_tasks = Table(
    "attack_chart_tasks",
    Base.metadata,
    Column(
        "chart_id",
        Integer,
        ForeignKey("attack_charts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "evaluation_task_id",
        Integer,
        ForeignKey("evaluation_tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

attack_chart_judge_runs = Table(
    "attack_chart_judge_runs",
    Base.metadata,
    Column(
        "chart_id",
        Integer,
        ForeignKey("attack_charts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "judge_task_run_id",
        Integer,
        ForeignKey("judge_task_runs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class AttackVisualizationRun(Base):
    """
    Stores a multi-run or single-run Attack Visualization & Statistical Analysis report
    (Coverage, Disinfo Classification, Heatmaps, Trade-offs, Language Gap, Radar,
    Vulnerability Ranking, Cross-Case Comparison, Alignment Robustness Index (ARI),
    Factorial ANOVA, and SRD/DnE/DnM/WSM/TOPSIS MCDM Ranking).
    Linked many-to-many with `EvaluationTask` via `attack_visualization_run_tasks`.
    """
    __tablename__ = "attack_visualization_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exclude_russian = Column(Boolean, default=True, nullable=False)

    # Full statistical & analytical summary tables (ARI, ANOVA, MCDM, coverage, interpretation)
    summary_payload = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    evaluation_tasks = relationship(
        "EvaluationTask",
        secondary=attack_visualization_run_tasks,
        back_populates="attack_visualization_runs",
    )
    charts = relationship(
        "AttackChart",
        back_populates="visualization_run",
        cascade="all, delete-orphan",
    )


class AttackChart(Base):
    """
    Stores an individual generated chart / figure for Attack & Judge Evaluation results,
    with M2M links to the contributing `EvaluationTask`s and `JudgeTaskRun`s.
    """
    __tablename__ = "attack_charts"

    id = Column(Integer, primary_key=True, index=True)
    visualization_run_id = Column(
        Integer,
        ForeignKey("attack_visualization_runs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    chart_type = Column(String(80), index=True, nullable=False)
    task_scope = Column(String(80), index=True, nullable=True, default="all")
    title = Column(String(255), nullable=False)
    subtitle = Column(Text, nullable=True)

    # Structured series/matrix/axis payload for interactive rendering
    chart_data = Column(JSON, default=dict, nullable=False)

    # Publication-ready vector SVG representation of the chart
    svg_content = Column(Text, nullable=True)

    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    visualization_run = relationship("AttackVisualizationRun", back_populates="charts")
    evaluation_tasks = relationship(
        "EvaluationTask",
        secondary=attack_chart_tasks,
        back_populates="attack_charts",
    )
    judge_task_runs = relationship(
        "JudgeTaskRun",
        secondary=attack_chart_judge_runs,
        back_populates="attack_charts",
    )
    artifact = relationship("Artifact")





class StressTestRun(Base):
    """
    One execution of the statistical stress test (`api_cv/services/stress_test`):
    Monte Carlo simulation of controlled classifier failure modes plus the reviewer
    analyses, publication figures and the results archive.

    The outputs live on disk in `results_dir` (under the shared `UPLOAD_DIR` volume, so both the
    API and the CV worker can reach them); the row only tracks configuration, status and progress.
    """
    __tablename__ = "stress_test_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)

    celery_task_id = Column(String, nullable=True)
    status = Column(SQLEnum(TaskStatus, name="task_status_enum"), default=TaskStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)

    # Simulation design (StressTestConfig fields) and the requested pipeline steps / figure options
    config = Column(JSON, default=dict, nullable=False)
    steps = Column(JSON, default=list, nullable=False)

    # Current pipeline step ("simulate", "reviewer", "figures", "archive") and its progress in percent
    stage = Column(String(50), nullable=True)
    progress = Column(Float, default=0.0, nullable=False)

    # Crash handling: attempt number (1 = first run) and reviewer parallelism (NULL = all cores).
    # After a worker crash / OOM the run is retried once with n_jobs=1 (stress_test_worker.py).
    attempt = Column(Integer, default=1, server_default="1", nullable=False)
    n_jobs = Column(Integer, nullable=True)

    results_dir = Column(String, nullable=True)
    archive_path = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def has_archive(self) -> bool:
        return bool(self.archive_path)

    @classmethod
    def get_paginated(cls, db: Session, page: int, size: int):
        """Returns (items, total_count, pages), newest first."""
        total_count = db.query(cls).count()
        items = db.query(cls).order_by(cls.id.desc()).offset((page - 1) * size).limit(size).all()
        pages = math.ceil(total_count / size) if total_count > 0 else 1
        return items, total_count, pages

    @classmethod
    def get_by_id(cls, db: Session, run_id: int):
        return db.query(cls).filter(cls.id == run_id).first()
