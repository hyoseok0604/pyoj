from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.user import User, UserConstraints
from web.schemas.user import CreateUserRequestSchema as CreateUserSchema
from web.services.exception import ServiceException


@as_annotated_dependency
class UserService:
    def __init__(self, session: AsyncSessionDependency) -> None:
        self.session = session

    async def create(self, schema: CreateUserSchema) -> User:
        user = schema.model_dump()

        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as e:
            error = e.orig
            if error is not None and isinstance(error, UniqueViolation):
                if error.diag.constraint_name == UserConstraints.USERNAME_UNIQUE.value:
                    raise DuplicatedUsername() from e

            raise e

        return user

    async def get_user_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)

        user = await self.session.scalar(stmt)

        return user

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)

        user = await self.session.scalar(stmt)

        return user


class DuplicatedUsername(ServiceException):
    def __init__(self) -> None:
        super().__init__({"username": "이미 존재하는 아이디입니다."})
