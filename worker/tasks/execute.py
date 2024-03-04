import os
import pathlib

from celery.exceptions import Reject
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from judger.execute import execute
from web.models.problem import Testcase
from web.models.submission import Submission, SubmissionTestcaseResult
from web.models.systemcall import Systemcall, SystemcallCount, SystemcallGroup
from worker.database import DatabaseSession
from worker.settings import settings


def execute_testcase(submission_id: int, testcase_id: int):
    with DatabaseSession() as session:
        submission = _get_submission_or_reject(session=session, id=submission_id)
        testcase = _get_testcase_or_reject(session=session, id=testcase_id)
        systemcall_group = _get_systemcall_group_or_reject(session=session)

        root = pathlib.Path(settings.judge_file_path)

        if not root.exists():
            raise Reject("Root judge file directory is not exist.")

        submission_path = root / "submissions" / f"{submission_id}"

        if submission is None:
            raise Reject("Submission not found.")

        # stdin, stdout, stderr files
        if testcase_id == -1:
            testcase_file = os.devnull
        elif testcase is not None:
            testcase_file = str(
                (
                    root / f"{testcase.problem_id}" / "testcases" / f"{testcase.id}.in"
                ).resolve()
            )
        else:
            raise Reject("Testcase not found.")
        stdout_file = submission_path / f"{testcase_id}.out"
        stderr_file = submission_path / f"{testcase_id}.err"

        # systemcall allowed
        # systemcall_count_limits = {
        #     systemcall_count_limit.systemcall.number: systemcall_count_limit.count
        #     for systemcall_count_limit in submission.language.systemcall_count_limits
        # }
        systemcall_count_limits = {
            systemcall.number: -1 for systemcall in systemcall_group.systemcalls
        }

        result, time, memory, systemcall_counts = execute(
            working_directory=str(submission_path.resolve()),
            execute_command=submission.language.execute_command,
            stdin_filename=testcase_file,
            stdout_filename=str(stdout_file.resolve()),
            stderr_filename=str(stderr_file.resolve()),
            time_limit=submission.problem.time_limit
            if submission.problem is not None
            else 1000,
            memory_limit=submission.problem.memory_limit * 1024 * 1024
            if submission.problem is not None
            else 256 * 1024 * 1024,
            output_limit=16 * 1024 * 1024,
            systemcall_count_limits=systemcall_count_limits,
        )

        testcase_results_stmt = (
            select(SubmissionTestcaseResult)
            .where(SubmissionTestcaseResult.submission_id == submission_id)
            .with_for_update()
        )

        testcase_results = session.scalars(testcase_results_stmt)

        for testcase_result in testcase_results:
            if (
                testcase_result.testcase_id is not None
                and testcase_result.testcase_id != testcase_id
            ):
                continue

            if testcase_result.testcase_id is None and testcase_id != -1:
                continue

            testcase_result.result = result
            testcase_result.time = time
            testcase_result.memory = memory

            with open(stdout_file) as f:
                testcase_result.stdout = f.read()

            with open(stderr_file) as f:
                testcase_result.stderr = f.read()

            insert_systemcallcounts_stmt = insert(SystemcallCount).values(
                [
                    {
                        SystemcallCount.submission_result_id: testcase_result.id,
                        SystemcallCount.systemcall_id: select(Systemcall.id)
                        .where(Systemcall.systemcall_group_id == systemcall_group.id)
                        .where(Systemcall.number == number),
                        SystemcallCount.count: count,
                    }
                    for number, count in systemcall_counts.items()
                ]
            )
            session.execute(insert_systemcallcounts_stmt)

            session.commit()


def _get_submission_or_reject(session: Session, id: int) -> Submission:
    submission = session.get(Submission, id)

    if submission is None:
        raise Reject("Cannot found submission.")

    return submission


def _get_testcase_or_reject(session: Session, id: int) -> Testcase:
    testcase = session.get(Testcase, id)

    if testcase is None:
        raise Reject("Cannot found testcase.")

    return testcase


def _get_systemcall_group_or_reject(session: Session) -> SystemcallGroup:
    systemcall_group_stmt = (
        select(SystemcallGroup)
        .where(SystemcallGroup.is_enabled.is_(True))
        .join(SystemcallGroup.systemcalls)
    )
    systemcall_group = session.scalar(systemcall_group_stmt)

    if systemcall_group is None:
        raise Reject("Cannot found enabled systemcall group.")

    return systemcall_group
