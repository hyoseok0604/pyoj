from datetime import datetime
from typing import Optional

from web.models.problem import Problem
from web.schemas.base import BaseSchema, Creator, SerializeToModelSchema
from web.schemas.pagination import PaginationSchema
from web.schemas.problem.types import Description, MemoryLimit, TimeLimit
from web.schemas.sort import SortSchema


class BaseProblemWithoutCreator(BaseSchema):
    title: str
    time_limit: TimeLimit
    memory_limit: MemoryLimit
    created_at: datetime
    is_public: bool


class BaseProblem(BaseProblemWithoutCreator):
    creator: Optional[Creator]


class Descriptions(BaseSchema):
    description: Description
    input_description: Description
    output_description: Description
    limit_description: Description


class CreateProblemRequestSchema(SerializeToModelSchema[Problem]):
    title: str
    time_limit: TimeLimit
    memory_limit: MemoryLimit
    description: Description
    input_description: Description
    output_description: Description
    limit_description: Description

    def serialize(self) -> Problem:
        problem = Problem()

        problem.title = self.title
        problem.time_limit = self.time_limit
        problem.memory_limit = self.memory_limit
        problem.description = self.description
        problem.input_description = self.input_description
        problem.output_description = self.output_description
        problem.limit_description = self.limit_description

        return problem


class CreateProblemResponseSchema(BaseProblem, Descriptions):
    id: int


class GetProblemResponseSchema(BaseProblem, Descriptions):
    id: int


class GetProblemsRequestSchema(PaginationSchema, SortSchema):
    title: Optional[str] = None
    creator: Optional[str] = None
    is_public: bool = False


class GetProblemsResponseSchema(BaseProblem):
    id: int


class UpdateProblemRequestSchema(SerializeToModelSchema[Problem]):
    title: Optional[str] = None
    time_limit: Optional[TimeLimit] = None
    memory_limit: Optional[MemoryLimit] = None
    description: Optional[Description] = None
    input_description: Optional[Description] = None
    output_description: Optional[Description] = None
    limit_description: Optional[Description] = None
    is_public: Optional[bool] = None

    def serialize(self) -> Problem:
        problem = Problem()

        if self.title is not None:
            problem.title = self.title

        if self.time_limit is not None:
            problem.time_limit = self.time_limit

        if self.memory_limit is not None:
            problem.memory_limit = self.memory_limit

        if self.description is not None:
            problem.description = self.description

        if self.input_description is not None:
            problem.input_description = self.input_description

        if self.output_description is not None:
            problem.output_description = self.output_description

        if self.limit_description is not None:
            problem.limit_description = self.limit_description

        if self.is_public is not None:
            problem.is_public = self.is_public

        return problem


class UpdateProblemResponseSchema(BaseProblem, Descriptions):
    id: int
