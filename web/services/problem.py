from typing import Literal, Sequence, overload

from sqlalchemy import select
from sqlalchemy.orm import selectinload, undefer_group

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.problem import Problem
from web.models.user import SessionUser, User
from web.schemas.problem import CreateProblemRequestSchema as CreateProblemSchema
from web.schemas.problem import GetProblemsRequestSchema, UpdateProblemRequestSchema
from web.services.exceptions import (
    AuthException,
    LoginRequiredException,
    NotFoundException,
    PermissionException,
    ServiceException,
)


@as_annotated_dependency
class ProblemService:
    def __init__(self, session: AsyncSessionDependency) -> None:
        self.session = session

    async def create(
        self, session_user: SessionUser | None, schema: CreateProblemSchema
    ) -> Problem:
        if session_user is None:
            raise AuthException()

        problem = schema.model_dump()

        problem.creator = session_user.user

        self.session.add(problem)
        await self.session.commit()
        await self.session.refresh(problem)

        return await self.get_problem_by_id(problem.id, raise_none=True)

    @overload
    async def get_problem_by_id(
        self, id: int, raise_none: Literal[True] = ...
    ) -> Problem:
        ...

    @overload
    async def get_problem_by_id(
        self, id: int, raise_none: Literal[False]
    ) -> Problem | None:
        ...

    async def get_problem_by_id(
        self, id: int, raise_none: bool = False
    ) -> Problem | None:
        stmt = (
            select(Problem)
            .where(Problem.id == id)
            .options(
                selectinload(Problem.creator), undefer_group("problem_descriptions")
            )
        )

        problem = await self.session.scalar(stmt)

        if raise_none and problem is None:
            raise ServiceException()

        return problem

    async def get_problems(self, schema: GetProblemsRequestSchema) -> Sequence[Problem]:
        stmt = (
            select(Problem)
            .limit(schema.count)
            .offset(schema.offset)
            .order_by(Problem.id.desc() if schema.sort == "desc" else Problem.id.asc())
            .where(Problem.is_public.is_(schema.is_public))
            .options(selectinload(Problem.creator))
        )

        if schema.title is not None:
            stmt = stmt.where(Problem.title.like(f"%{schema.title}%"))

        if schema.creator is not None:
            stmt = stmt.where(User.username == schema.creator)

        problems = (await self.session.scalars(stmt)).all()

        return problems

    async def update_problem(
        self,
        id: int,
        session_user: SessionUser | None,
        schema: UpdateProblemRequestSchema,
    ):
        problem = await self.session.get(
            Problem,
            id,
            options=[
                selectinload(Problem.creator),
                undefer_group("problem_descriptions"),
            ],
        )

        if session_user is None:
            raise LoginRequiredException()

        if problem is None:
            raise NotFoundException()

        if problem.creator.id != session_user.user.id:
            raise PermissionException()

        new_problem = schema.model_dump()
        new_problem.id = id
        await self.session.merge(new_problem)
        await self.session.commit()

        return await self.get_problem_by_id(id, raise_none=True)

    async def delete_problem(self, id: int, session_user: SessionUser | None):
        if session_user is None:
            raise LoginRequiredException()

        problem = await self.get_problem_by_id(id)

        if problem is None:
            raise NotFoundException()

        if session_user.user.id != problem.creator.id:
            raise PermissionException()

        await self.session.delete(problem)
        await self.session.commit()
