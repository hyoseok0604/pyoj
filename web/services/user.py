from psycopg.errors import UniqueViolation
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import undefer

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.user import USERNAME_UNIQUE_CONSTRAINT_NAME, SessionUser, User
from web.schemas.user import CreateUserRequestSchema as CreateUserSchema
from web.services.exceptions import (
    LoginRequiredException,
    PermissionException,
    UsernameDuplicated,
)


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
                if error.diag.constraint_name == USERNAME_UNIQUE_CONSTRAINT_NAME:
                    raise UsernameDuplicated() from e

            raise e

        return user

    async def get_user_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)

        user = await self.session.scalar(stmt)

        return user

    async def get_user_by_username(
        self, username: str, with_password: bool = False
    ) -> User | None:
        stmt = select(User).where(User.username == username)

        if with_password:
            stmt = stmt.options(undefer(User.password))

        user = await self.session.scalar(stmt)

        return user

    async def delete_user_by_id(
        self, id: int, session_user: SessionUser | None
    ) -> User | None:
        if session_user is None:
            raise LoginRequiredException()

        if session_user.user.id != id:
            raise PermissionException()

        stmt = delete(User).where(User.id == id).returning(User)

        user = await self.session.scalar(stmt)
        await self.session.commit()

        return user
