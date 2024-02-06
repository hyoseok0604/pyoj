from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.user import SessionUser as PostgresSessionUser
from web.services.exceptions import VerifySessionFailed
from web.services.session.base import AbstractSessionService


@as_annotated_dependency
class PostgresSessionService(AbstractSessionService[PostgresSessionUser]):
    def __init__(self, session: AsyncSessionDependency) -> None:
        self.session = session

    async def create_session(self, session_data: PostgresSessionUser):
        session_key = self._generate_session_key()
        session_data.session_key = session_key

        self.session.add(session_data)
        await self.session.commit()
        await self.session.refresh(session_data)

        return session_key

    async def verify_session(self, session_key: str) -> PostgresSessionUser:
        stmt = (
            select(PostgresSessionUser)
            .where(PostgresSessionUser.session_key == session_key)
            .options(selectinload(PostgresSessionUser.user))
        )

        session_user = await self.session.scalar(stmt)

        if session_user is None:
            raise VerifySessionFailed()

        return session_user

    async def delete_session(self, session_key: str) -> bool:
        stmt = delete(PostgresSessionUser).where(
            PostgresSessionUser.session_key == session_key
        )

        result = await self.session.execute(stmt)

        return result.rowcount > 0

    async def delete_all_sessions_by_user_id(self, id: int):
        pass
