import bcrypt

from web.core.database import AsyncRedisDependency, AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.user import SessionUser
from web.schemas.auth import LoginRequestSchema
from web.services.exceptions import (
    UserameOrPasswordMismatched,
)
from web.services.session.postgres import PostgresSessionService
from web.services.user import UserService


@as_annotated_dependency
class AuthService:
    def __init__(
        self,
        session: AsyncSessionDependency,
        redis: AsyncRedisDependency,
        user_service: UserService,
        session_service: PostgresSessionService,
    ) -> None:
        self.session = session
        self.redis = redis
        self.user_service = user_service
        self.session_service = session_service

    async def login(self, schema: LoginRequestSchema):
        user = await self.user_service.get_user_by_username(
            schema.username, with_password=True
        )

        if user is None or not bcrypt.checkpw(
            schema.password.encode(), user.password.encode()
        ):
            raise UserameOrPasswordMismatched()

        session_user = SessionUser()
        session_user.user = user

        session_key = await self.session_service.create_session(session_user)

        return session_key

    async def verify(self, session_key: str):
        return await self.session_service.verify_session(session_key)

    async def logout(self, session_key: str):
        return await self.session_service.delete_session(session_key)
