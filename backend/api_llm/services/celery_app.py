import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "visionmetrics_llm",
    broker=redis_url,
    backend=redis_url,
    include=[
        "api_llm.services.worker",
        "api_llm.services.chat_worker",
        "api_llm.judge.worker"
    ]
)

celery_app.conf.task_routes = {
    'llm.evaluation': {'queue': 'llm_tasks'},
    'llm.judge.evaluation': {'queue': 'judge_tasks'},
    'chat.generate_text': {'queue': 'chat_tasks'}
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_time_limit=86400,
    task_soft_time_limit=86000
)