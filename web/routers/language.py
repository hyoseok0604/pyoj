from typing import Optional

from fastapi import APIRouter, Query

from web.schemas.language import (
    GetLanguageResponseSchema,
    GetLanguagesRequestSchema,
    GetLanguagesResponseSchema,
)
from web.services.language import LanguageService

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
