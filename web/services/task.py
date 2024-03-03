from celery import chain, group

from web.core.decorators import as_annotated_dependency
from web.logger import _log
from web.models.submission import Submission
from worker.tasks import (
    compile_submission_task,
    execute_testcase_task,
    parse_systemcalls_task,
)


@as_annotated_dependency
class TaskService:
    def request_parse_systemcall_task(self):
        parse_systemcalls_task.delay()  # type: ignore

    async def request_compile_and_run_submission_task(self, submission: Submission):
        if submission.problem is None:
            _log.info("Problem is not found. Run submission with empty input.")
            testcase_ids = [-1]
        else:
            testcase_ids = [testcase.id for testcase in submission.problem.testcases]

        chain(
            compile_submission_task.si(submission.id),  # type: ignore
            group(
                [
                    execute_testcase_task.si(submission.id, testcase_id)
                    for testcase_id in testcase_ids
                ]
            ),  # type: ignore
        ).delay()  # type: ignore
