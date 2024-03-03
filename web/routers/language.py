from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from web.core.dependencies import SessionUserDependency
from web.schemas.language import (
    GetLanguageResponseSchema,
    GetLanguagesRequestSchema,
    GetLanguagesResponseSchema,
)
from web.schemas.submission import (
    CreateLanguageSubmissionRequestSchema,
    CreateLanguageSubmissionResponseSchema,
    CreateSubmissionSchema,
    GetLanguageSubmissionsRequestSchema,
    GetLanguageSubmissionsResponseSchema,
    GetSubmissionsSchema,
)
from web.services.language import LanguageService
from web.services.submission import SubmissionService

api_router = APIRouter(prefix="/languages")


@api_router.get("", response_model=GetLanguagesResponseSchema)
async def get_languages_api(
    language_service: LanguageService,
    display_name: Optional[str] = Query(default=None),
    enabled_only: bool = Query(default=True),
):
    schema = GetLanguagesRequestSchema(
        display_name=display_name, enabled_only=enabled_only
    )

    languages = await language_service.get_languages(schema)

    return languages


@api_router.get("/{id}", response_model=GetLanguageResponseSchema)
async def get_language_api(language_service: LanguageService, id: int):
    languages = await language_service.get_language(id)

    return languages


@api_router.post(
    "/{language_id}/submissions",
    response_model=CreateLanguageSubmissionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_language_submission_api(
    submission_service: SubmissionService,
    request_schema: CreateLanguageSubmissionRequestSchema,
    session_user: SessionUserDependency,
    language_id: int = Path(),
):
    if session_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    service_schema = CreateSubmissionSchema(
        **request_schema.model_dump(),
        language_id=language_id,
        creator_id=session_user.user_id,
    )

    submission = await submission_service.create_submission(service_schema)

    return submission


@api_router.get(
    "/{language_id}/submissions",
    response_model=GetLanguageSubmissionsResponseSchema,
)
async def get_language_submissions_api(
    submission_service: SubmissionService,
    language_id: int,
    schema: GetLanguageSubmissionsRequestSchema = Depends(),  # noqa: B008
):
    servie_schema = GetSubmissionsSchema(**schema.model_dump(), language_id=language_id)
    submissions = await submission_service.get_submissions(servie_schema)

    return submissions
