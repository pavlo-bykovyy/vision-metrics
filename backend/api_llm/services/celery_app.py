from shared.celery_factory import create_celery_app
from api_llm import queues as q


celery_app = create_celery_app(
    "visionmetrics_llm",
    include=[
        "api_llm.services.worker",
        "api_llm.workers.chat.chat_worker",
        "api_llm.judge.worker",
        "api_llm.workers.attacks.attack_worker",
        "api_llm.workers.attacks.judge_worker",
    ],
    task_routes={
        q.LLM_EVALUATION_TASK: {"queue": q.LLM_QUEUE},
        q.JUDGE_EVALUATION_TASK: {"queue": q.JUDGE_EVALUATION_QUEUE},
        q.CHAT_TASK: {"queue": q.CHAT_QUEUE},
        q.ATTACK_DATASET_TASK: {"queue": q.ATTACK_DATASET_QUEUE},
        q.ATTACK_GENERATION_TASK: {"queue": q.ATTACK_GENERATION_QUEUE},
        q.ATTACK_JUDGE_TASK: {"queue": q.ATTACK_JUDGE_QUEUE},
    },
)