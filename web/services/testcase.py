from tempfile import SpooledTemporaryFile
from typing import Sequence

from sqlalchemy import select

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.core.settings import settings
from web.models.problem import Testcase
from web.models.user import SessionUser
from web.schemas.testcase import GetTestcasesRequestSchema
from web.services.exceptions import (
    InternalServerException,
    LoginRequiredException,
    NotFoundException,
    PermissionException,
    ServiceException,
)
from web.services.file import FileService
from web.services.problem import ProblemService


@as_annotated_dependency
class TestcaseService:
    def __init__(
        self,
        session: AsyncSessionDependency,
        problem_service: ProblemService,
        judge_file_service: FileService,
    ) -> None:
        self.session = session
        self.problem_service = problem_service
        self.judge_file_service = judge_file_service
        self.judge_file_path = settings.judge_file_path

    async def create_testcase(
        self,
        id: int,
        input_filename: str | None,
        output_filename: str | None,
        input_file: SpooledTemporaryFile[bytes],
        output_file: SpooledTemporaryFile[bytes],
        session_user: SessionUser | None,
    ):
        if session_user is None:
            raise LoginRequiredException()

        problem = await self.problem_service.get_problem_by_id(id)

        if problem is None:
            raise NotFoundException()

        if problem.creator_id != session_user.user_id:
            raise PermissionException()

        testcase = Testcase()
        testcase.problem = problem
        testcase.original_input_filename = (
            input_filename if input_filename is not None else ""
        )
        testcase.original_output_filename = (
            output_filename if output_filename is not None else ""
        )

        self.session.add(testcase)
        await self.session.flush()

        testcase_id = testcase.id

        try:
            input_size, output_size = self.judge_file_service.write_testcase_file(
                id, testcase_id, input_file, output_file
            )
            testcase.input_size = input_size
            testcase.output_size = output_size
        except ServiceException as e:
            await self.session.rollback()

            raise e
        except Exception as e:
            await self.session.rollback()

            raise InternalServerException(
                {"_details": "테스트 케이스 작성 중 오류가 발생했습니다."}
            ) from e

        testcase.input_preview = self._generate_testcase_preview(input_file).decode()
        testcase.output_preview = self._generate_testcase_preview(output_file).decode()
        await self.session.merge(testcase)

        await self.session.commit()
        await self.session.refresh(testcase)

        return testcase

    def _generate_testcase_preview(self, file: SpooledTemporaryFile[bytes]):
        file.seek(0)
        content = file.readlines()
        preview: list[bytes] = []

        for line in content:
            strip = line.strip()

            if len(strip) != 0:
                if len(strip) > 50:
                    strip = strip[:50] + b"..."
                preview.append(strip)

            if len(preview) == 10:
                break

        return b"\n".join(preview)

    async def get_testcase(self, testcase_id: int, problem_id: int):
        stmt = (
            select(Testcase)
            .where(Testcase.id == testcase_id)
            .where(Testcase.problem_id == problem_id)
        )

        testcase = await self.session.scalar(stmt)

        if testcase is None:
            raise NotFoundException()

        return testcase

    async def get_testcases(
        self, schema: GetTestcasesRequestSchema
    ) -> Sequence[Testcase]:
        stmt = (
            select(Testcase)
            .where(Testcase.problem_id == schema.problem_id)
            .limit(schema.count)
            .offset(schema.offset)
        )

        order_by = None
        if schema.order_by == "id":
            order_by = Testcase.id
        elif schema.order_by == "input_size":
            order_by = Testcase.input_size
        elif schema.order_by == "output_size":
            order_by = Testcase.output_size

        if order_by is None:  # pragma: no cover
            raise ServiceException()

        if schema.sort == "asc":
            stmt = stmt.order_by(order_by.asc())
        elif schema.sort == "desc":
            stmt = stmt.order_by(order_by.desc())

        testcases = (await self.session.scalars(stmt)).all()

        return testcases

    async def delete_testcase(
        self, testcase_id: int, problem_id: int, session_user: SessionUser | None
    ):
        if session_user is None:
            raise LoginRequiredException()

        testcase = await self.get_testcase(testcase_id, problem_id)

        if session_user.user_id != testcase.problem.creator_id:
            raise PermissionException()

        self.judge_file_service.delete_testcase_file(testcase.problem_id, testcase_id)

        await self.session.delete(testcase)
        await self.session.commit()
