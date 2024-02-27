from sqlalchemy import select, update
from sqlalchemy.orm import Session

from judger.language import languages as judger_languages
from web.core.database import async_session
from web.core.migration import migration
from web.logger import (
    DisableSqlalchemyLogger,
    _log,
)
from web.models.base import BaseModel
from web.models.language import Language


async def startup_migration():
    with DisableSqlalchemyLogger():
        async with async_session() as session:

            def wrapped_migration(session: Session):
                migration(session.connection(), BaseModel.metadata)

            await session.run_sync(wrapped_migration)
            await session.commit()


async def startup_language_migration():
    with DisableSqlalchemyLogger():
        async with async_session() as session:
            _log.info(f"{len(judger_languages)} languages detected.")

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
                    _log.info(f"Create language {language.display_name}.")
                else:
                    await session.merge(language)
                    _log.info(f"Update language {language.display_name}.")

            stmt = (
                update(Language)
                .where(
                    Language.display_name.not_in(
                        v.display_name for v in judger_languages
                    )
                )
                .values({Language.is_enabled: False})
            )

            result = await session.execute(stmt)
            _log.info(f"Disable {result.rowcount} languages.")
            await session.commit()


startup_functions = [startup_migration, startup_language_migration]
