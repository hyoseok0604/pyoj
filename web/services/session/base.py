import datetime
import secrets
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractSessionService(Generic[T], ABC):
    session_timeout = datetime.timedelta(days=14)

    @abstractmethod
    async def create_session(self, session_data: T) -> str:
        ...

    @abstractmethod
    async def verify_session(self, session_key: str) -> T:
        ...

    @abstractmethod
    async def delete_session(self, session_key: str) -> bool:
        ...

    @abstractmethod
    async def delete_all_sessions_by_user_id(self, id: int):
        ...

    def _generate_session_key(self):
        return secrets.token_urlsafe()
