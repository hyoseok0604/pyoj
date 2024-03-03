from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.submission import Submission, SubmissionTestcaseResult
from web.schemas.submission import CreateSubmissionSchema, GetSubmissionsSchema
from web.services.exceptions import NotFoundException
from web.services.task import TaskService


@as_annotated_dependency
class SubmissionService:
    def __init__(
        self, session: AsyncSessionDependency, task_service: TaskService
    ) -> None:
        self.session = session
        self.task_service = task_service

    async def create_submission(
        self,
        schema: CreateSubmissionSchema,
    ):
        submission = schema.model_dump()

        self.session.add(submission)

        await self.session.commit()
        await self.session.refresh(
            submission, attribute_names=["problem", "submission_results"]
        )
        await self.session.refresh(submission.problem, attribute_names=["testcases"])

        if submission.problem is not None:
            submission.submission_results = [
                SubmissionTestcaseResult(testcase_id=testcase.id)
                for testcase in submission.problem.testcases
            ]
        else:
            submission.submission_results = [SubmissionTestcaseResult()]
        await self.session.commit()

        await self.task_service.request_compile_and_run_submission_task(submission)

        return submission

    async def get_submission(self, submission_id: int):
        stmt = select(Submission).where(Submission.id == submission_id)

        submission = await self.session.scalar(stmt)

        if submission is None:
            raise NotFoundException()

        return submission

    async def get_submissions(
        self, schema: GetSubmissionsSchema
    ) -> Sequence[Submission]:
        stmt = (
            select(Submission)
            .offset(schema.offset)
            .limit(schema.count)
            .options(
                selectinload(Submission.creator),
                selectinload(Submission.language),
                selectinload(Submission.problem),
            )
        )

        if schema.language_id is not None:
            stmt = stmt.where(Submission.language_id == schema.language_id)

        if schema.problem_id is not None:
            stmt = stmt.where(Submission.problem_id == schema.problem_id)

        if schema.creator_id is not None:
            stmt = stmt.where(Submission.creator_id == schema.creator_id)

        submissions = (await self.session.scalars(stmt)).all()

        return submissions
