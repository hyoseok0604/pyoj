# For tasks
import logging

from judger.utils.system_call import parse_systemcall_x86_64_linux_gnu
from worker import celery_app
from worker.backends import redis_backend_with_database
from worker.settings import settings

_log = logging.getLogger()


@celery_app.task(
    max_retries=0,
    backend=redis_backend_with_database(
        app=celery_app, redis_url=str(settings.redis_uri), db=1
    ),
)
def parse_systemcalls():
    return parse_systemcall_x86_64_linux_gnu()
