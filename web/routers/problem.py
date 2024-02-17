from tempfile import SpooledTemporaryFile
from typing import Literal, Optional, cast

from fastapi import APIRouter, Query, UploadFile, status

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
from web.schemas.testcase import (
    CreateTestcaseResponseSchema,
    GetTestcaseResponseSchema,
    GetTestcasesRequestSchema,
    GetTestcasesResponseSchema,
)
from web.services.file import FileService
from web.services.problem import ProblemService
from web.services.testcase import TestcaseService

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


@api_router.post(
    "/{id}/testcases",
    response_model=CreateTestcaseResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_problem_testcase_api(
    id: int,
    input_file: UploadFile,
    output_file: UploadFile,
    service: TestcaseService,
):
    testcase = await service.create_testcase(
        id,
        input_file.filename,
        output_file.filename,
        cast(SpooledTemporaryFile[bytes], input_file.file),
        cast(SpooledTemporaryFile[bytes], output_file.file),
    )

    return testcase


@api_router.get(
    "/{problem_id}/testcases", response_model=list[GetTestcasesResponseSchema]
)
async def get_problem_testcases_api(
    testcase_service: TestcaseService,
    problem_id: int,
    page: int = Query(default=1, ge=1),
    order_by: Literal["id", "input_size", "output_size"] = Query(default="id"),
    count: int = Query(default=20, ge=1, le=100),
    sort: Literal["asc", "desc"] = Query(default="desc"),
):
    schema = GetTestcasesRequestSchema(
        sort=sort, page=page, count=count, problem_id=problem_id, order_by=order_by
    )
    testcases = await testcase_service.get_testcases(schema)

    return testcases


@api_router.get(
    "/{problem_id}/testcases/{testcase_id}", response_model=GetTestcaseResponseSchema
)
async def get_problem_testcase_api(
    problem_id: int,
    testcase_id: int,
    testcase_service: TestcaseService,
    judge_file_service: FileService,
):
    testcase = await testcase_service.get_testcase(testcase_id)
    input, output = judge_file_service.read_testcase_file(problem_id, testcase_id)

    return {
        "id": testcase.id,
        "problem_id": testcase.problem_id,
        "input": input,
        "output": output,
    }
