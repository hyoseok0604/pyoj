from typing import Sequence

from sqlalchemy import select

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.language import Language
from web.schemas.language import GetLanguagesRequestSchema


@as_annotated_dependency
class LanguageService:
    def __init__(self, session: AsyncSessionDependency) -> None:
        self.session = session

    async def get_languages(
        self, schema: GetLanguagesRequestSchema
    ) -> Sequence[Language]:
        stmt = select(Language)

        if schema.display_name is not None:
            stmt = stmt.where(Language.display_name.ilike(f"%{schema.display_name}%"))

        if schema.enabled_only is not None:
            stmt = stmt.where(Language.is_enabled.is_(True))

        languages = (await self.session.scalars(stmt)).all()

        return languages

    async def get_language(self, id: int) -> Language | None:
        stmt = select(Language).where(Language.id == id)

        language = await self.session.scalar(stmt)

        return language
