import json
from typing import Any, Coroutine, cast

from pydantic_core import ValidationError

from web.core.database import AsyncRedisDependency
from web.core.decorators import as_annotated_dependency
from web.schemas.auth import SessionUser as RedisSessionUser
from web.services.exceptions import CreateSessionFailed, VerifySessionFailed
from web.services.session.base import AbstractSessionService


@as_annotated_dependency
class RedisSessionService(AbstractSessionService[RedisSessionUser]):
    def __init__(self, redis: AsyncRedisDependency) -> None:
        self.redis = redis

    async def create_session(self, session_data: RedisSessionUser):
        session_key = self._generate_session_key()

        result = await cast(
            Coroutine[Any, Any, int],
            self.redis.hset(
                session_key,
                "session_data",
                json.dumps({"id": session_data.id, "username": session_data.username}),
            ),
        )

        if result == 0:
            raise CreateSessionFailed()

        await self.redis.expire(session_key, self.session_timeout, nx=True)

        return session_key

    async def verify_session(self, session_key: str) -> RedisSessionUser:
        session_data = await cast(
            Coroutine[Any, Any, str | None],
            self.redis.hget(session_key, "session_data"),
        )

        if session_data is None:
            raise VerifySessionFailed()

        try:
            session_data_dict = json.loads(session_data)
            session_user = RedisSessionUser(**session_data_dict)

            return session_user
        except ValidationError as e:
            raise VerifySessionFailed() from e

    async def delete_session(self, session_key: str) -> bool:
        result = await cast(
            Coroutine[Any, Any, int],
            self.redis.hdel(session_key, "session_data"),  # type: ignore
        )

        return result == 1
