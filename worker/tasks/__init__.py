from web import models
from worker import celery_app
from worker.backends import redis_backend_with_database
from worker.settings import settings
from worker.tasks.compile import compile_submission
from worker.tasks.execute import execute_testcase
from worker.tasks.parse_systemcall import parse_systemcalls


@celery_app.task(
    max_retries=0,
    backend=redis_backend_with_database(
        app=celery_app, redis_url=str(settings.redis_uri), db=1
    ),
)
def parse_systemcalls_task():
    parse_systemcalls()


@celery_app.task(max_retries=0)
def compile_submission_task(submission_id: int):
    compile_submission(submission_id)


@celery_app.task(max_retries=0)
def execute_testcase_task(submission_id: int, language_id: int):
    execute_testcase(submission_id, language_id)
