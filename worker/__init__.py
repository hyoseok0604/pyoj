from celery import Celery  # type: ignore[reportMissingTypeStubs]

from worker.settings import settings

celery_app = Celery(
    "worker",
    broker=str(settings.rabbitmq_uri),
    broker_connection_retry_on_startup=True,
    result_extended=True,
    backend=str(settings.redis_uri),
)

celery_app.autodiscover_tasks(["worker"])  # type: ignore[reportUnknownMemberType]
