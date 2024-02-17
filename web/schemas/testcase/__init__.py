from typing import Literal

from web.schemas.base import BaseSchema
from web.schemas.pagination import PaginationSchema
from web.schemas.sort import SortSchema


class CreateTestcaseResponseSchema(BaseSchema):
    id: int
    problem_id: int
    original_input_filename: str
    original_output_filename: str
    input_preview: str
    output_preview: str
    input_size: int
    output_size: int


class GetTestcaseResponseSchema(BaseSchema):
    id: int
    problem_id: int
    original_input_filename: str
    original_output_filename: str
    input_preview: str
    output_preview: str
    input_size: int
    output_size: int


class GetTestcasesRequestSchema(PaginationSchema, SortSchema):
    problem_id: int
    order_by: Literal["id", "input_size", "output_size"] = "id"


class GetTestcasesResponseSchema(BaseSchema):
    id: int
    problem_id: int
    original_input_filename: str
    original_output_filename: str
    input_size: int
    output_size: int
