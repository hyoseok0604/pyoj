from typing import Literal, Optional

from fastapi import APIRouter, Query, status

from web.core.dependencies import SessionUserDependency
from web.schemas.problem import (
    CreateProblemRequestSchema,
    CreateProblemResponseSchema,
    GetProblemResponseSchema,
    GetProblemsRequestSchema,
    GetProblemsResponseSchema,
    UpdateProblemRequestSchema,
    UpdateProblemResponseSchema,
)
from web.services.problem import ProblemService

api_router = APIRouter(prefix="/problems")


@api_router.post(
    "", response_model=CreateProblemResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_problem_api(
    schema: CreateProblemRequestSchema,
    service: ProblemService,
    user: SessionUserDependency,
):
    problem = await service.create(user, schema)

    return problem


@api_router.get("/{id}", response_model=GetProblemResponseSchema)
async def get_problem_api(id: int, service: ProblemService):
    problem = await service.get_problem_by_id(id)

    return problem


@api_router.get("", response_model=list[GetProblemsResponseSchema])
async def get_problems_api(
    service: ProblemService,
    title: Optional[str] = Query(default=None),
    creator: Optional[str] = Query(default=None),
    is_public: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    count: int = Query(default=20, ge=1, le=100),
    sort: Literal["asc", "desc"] = Query(default="desc"),
):
    schema = GetProblemsRequestSchema(
        title=title,
        creator=creator,
        is_public=is_public,
        count=count,
        page=page,
        sort=sort,
    )
    problems = await service.get_problems(schema)

    return problems


@api_router.patch("/{id}", response_model=UpdateProblemResponseSchema)
async def update_problem_api(
    id: int,
    service: ProblemService,
    schema: UpdateProblemRequestSchema,
    user: SessionUserDependency,
):
    problem = await service.update_problem(id, user, schema)

    return problem


@api_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_problem_api(
    id: int, service: ProblemService, user: SessionUserDependency
):
    await service.delete_problem(id, user)
