from fastapi import APIRouter, status

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
async def get_problems_api(service: ProblemService, schema: GetProblemsRequestSchema):
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
