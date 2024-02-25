# For tasks


from worker import celery_app
from worker.backends import redis_backend_with_database
from worker.settings import settings
from worker.tasks.parse_systemcall import parse_systemcalls


@celery_app.task(
    max_retries=0,
    backend=redis_backend_with_database(
        app=celery_app, redis_url=str(settings.redis_uri), db=1
    ),
)
def parse_systemcalls_task():
    parse_systemcalls()
