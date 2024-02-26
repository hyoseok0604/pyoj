from sqlalchemy import select
from sqlalchemy.orm import Session

from judger.language import languages as judger_languages
from web.core.database import async_session
from web.core.migration import migration
from web.models.base import BaseModel
from web.models.language import Language


async def startup_migration():
    async with async_session() as session:

        def wrapped_migration(session: Session):
            migration(session.connection(), BaseModel.metadata)

        await session.run_sync(wrapped_migration)
        await session.commit()


async def startup_language_migration():
    async with async_session() as session:
        for judger_language in judger_languages:
            stmt = select(Language).where(
                Language.display_name == judger_language.display_name
            )

            language = await session.scalar(stmt)
            is_new = language is None

            if language is None:
                language = Language()

            language.display_name = judger_language.display_name
            language.filename = judger_language.filename
            language.compile_command = judger_language.compile_command
            language.execute_command = judger_language.execute_command

            if is_new:
                session.add(language)
            else:
                await session.merge(language)

            await session.commit()


startup_functions = [startup_migration, startup_language_migration]
