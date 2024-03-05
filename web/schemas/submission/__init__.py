from datetime import datetime
from typing import Optional

from fastapi import Query
from pydantic import field_validator

from web.models.submission import Submission
from web.schemas.base import (
    BaseSchema,
    Creator,
    Language,
    Problem,
    RootSchema,
    SerializeToModelSchema,
)
from web.schemas.pagination import PaginationSchema
from web.schemas.submission.types import Code


class BaseSubmission(BaseSchema):
    code: Code


class SubmissionRelation(BaseSchema):
    problem_id: Optional[int] = None
    language_id: int
    creator_id: int


class CreateSubmissionSchema(  # type: ignore
    SubmissionRelation, BaseSubmission, SerializeToModelSchema[Submission]
):
    def serialize(self):
        fields = ["code", "problem_id", "language_id", "creator_id"]

        language_submission = Submission(
            **{field: self.__getattribute__(field) for field in fields}
        )

        return language_submission


class CreateLanguageSubmissionRequestSchema(BaseSubmission):
    ...


class CreateLanguageSubmissionResponseSchema(BaseSubmission):
    id: int
    created_at: datetime


class GetLanguageSubmissionResponseSchema(BaseSubmission):
    id: int
    created_at: datetime

    problem: Optional[Problem]
    language: Language
    creator: Optional[Creator]


class GetSubmissionsSchema(PaginationSchema):
    problem_id: Optional[int] = None
    language_id: Optional[int] = None
    creator_id: Optional[int] = None


class GetLanguageSubmissionsRequestSchema(PaginationSchema):
    problem_id: Optional[int] = None
    creator_id: Optional[int] = None


class GetLanguageSubmissionsResponseSchema(RootSchema):
    root: list[GetLanguageSubmissionResponseSchema]


class CreateSubmissionRequestSchema(BaseSubmission):
    problem_id: int
    language_id: int


class CreateSubmissionResponseSchema(CreateSubmissionRequestSchema):
    id: int
    created_at: datetime
