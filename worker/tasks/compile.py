import pathlib

from celery.exceptions import Reject
from sqlalchemy import update

from judger.compile import compile
from judger.compile.result import CompileResult
from judger.execute.result import ExecuteResult
from web.models.submission import Submission, SubmissionTestcaseResult
from worker.database import DatabaseSession
from worker.logger import _log
from worker.settings import settings


def compile_submission(submission_id: int):
    with DatabaseSession() as session:
        submission = session.get(Submission, submission_id)

        if submission is None:
            raise Reject("Submission cannot found.")

        root = pathlib.Path(settings.judge_file_path)

        if not root.exists():
            raise Reject("Root judge file directory is not exist.")

        submission_path = root / "submissions" / f"{submission_id}"
        submission_path.mkdir(parents=True, exist_ok=True)

        submission_file = submission_path / submission.language.filename
        stdout_file = submission_path / "stdout.out"
        stderr_file = submission_path / "stderr.err"

        with open(submission_file, "w+") as f:
            f.write(submission.code)

        result = compile(
            str(submission_path.resolve()),
            submission.language.compile_command,
            10,
            str(stdout_file.resolve()),
            str(stderr_file.resolve()),
        )

        _log.info(f"Compile result : {result}")

        submission.compile_result = result

        with open(stdout_file) as stdout:
            submission.compile_stdout = stdout.read()

        with open(stderr_file) as stderr:
            submission.compile_stderr = stderr.read()

        if result == CompileResult.COMPILE_FAILURE:
            stmt = (
                update(SubmissionTestcaseResult)
                .where(SubmissionTestcaseResult.submission_id == submission_id)
                .values({SubmissionTestcaseResult.result: ExecuteResult.COMPILE_ERROR})
            )

            session.execute(stmt)

        session.commit()

        if result == CompileResult.COMPILE_FAILURE:
            raise Reject("Compile error.")
