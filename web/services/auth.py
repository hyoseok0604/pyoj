import datetime
import json
import secrets
from typing import Any, Coroutine, cast

import bcrypt
from pydantic import ValidationError

from web.core.database import AsyncRedisDependency, AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.schemas.auth import LoginRequestSchema, SessionUser
from web.services.exceptions import (
    CreateSessionFailed,
    LoginFailed,
    VerifySessionFailed,
)
from web.services.user import UserService


@as_annotated_dependency
class AuthService:
    def __init__(
        self,
        session: AsyncSessionDependency,
        redis: AsyncRedisDependency,
        user_service: UserService,
    ) -> None:
        self.session = session
        self.redis = redis
        self.user_service = user_service

        self.session_timeout = datetime.timedelta(days=14)

    async def login(self, schema: LoginRequestSchema):
        user = await self.user_service.get_user_by_username(schema.username)

        if user is None:
            raise LoginFailed()

        if not bcrypt.checkpw(schema.password.encode(), user.password.encode()):
            raise LoginFailed()

        session_key = await self.create_session(
            {"id": user.id, "username": user.username}
        )

        return session_key

    async def create_session(self, session_data: dict[str, str | int]):
        session_key = self.generate_session_key()

        result = await cast(
            Coroutine[Any, Any, int],
            self.redis.hset(session_key, "session_data", json.dumps(session_data)),
        )

        if result == 0:
            raise CreateSessionFailed()

        await self.redis.expire(session_key, self.session_timeout, nx=True)

        return session_key

    def generate_session_key(self):
        return secrets.token_urlsafe()

    async def verify_session(self, session_key: str) -> SessionUser:
        session_data = await cast(
            Coroutine[Any, Any, str | None],
            self.redis.hget(session_key, "session_data"),
        )

        if session_data is None:
            raise VerifySessionFailed()

        try:
            session_data_dict = json.loads(session_data)
            session_user = SessionUser(**session_data_dict)

            return session_user
        except ValidationError as e:
            raise VerifySessionFailed() from e

    async def delete_session(self, session_key: str) -> bool:
        result = await cast(
            Coroutine[Any, Any, int],
            self.redis.hdel(session_key, "session_data"),  # type: ignore
        )

        return result == 1
