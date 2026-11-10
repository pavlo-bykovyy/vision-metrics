import os
from celery import Celery


def create_celery_app(name: str, include: list[str], task_routes: dict) -> Celery:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

    app = Celery(name, broker=redis_url, backend=redis_url, include=include)
    app.conf.task_routes = task_routes
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        broker_connection_retry_on_startup=True,
        task_time_limit=86400,
        task_soft_time_limit=86000,
    )
    return app