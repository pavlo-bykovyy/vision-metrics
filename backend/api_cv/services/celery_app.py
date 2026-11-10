from shared.celery_factory import create_celery_app


celery_app = create_celery_app(
    "visionmetrics_cv",
    include=["api_cv.services.worker"],
    task_routes={"cv.*": {"queue": "cv_tasks"}},
)