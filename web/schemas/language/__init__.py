from typing import Optional

from web.schemas.base import BaseSchema, RootSchema


class Language(BaseSchema):
    id: int
    display_name: str
    filename: str
    compile_command: str
    execute_command: str
    is_enabled: bool


class GetLanguagesRequestSchema(BaseSchema):
    display_name: Optional[str] = None
    enabled_only: bool = True


class GetLanguagesResponseSchema(RootSchema):
    root: list[Language]


class GetLanguageResponseSchema(Language):
    ...
