import enum

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from web.models.base import BaseModel


class UserConstraints(enum.Enum):
    USERNAME_UNIQUE = "user_username_unique"


class User(BaseModel):
    __tablename__ = "user"

    __table_args__ = (
        UniqueConstraint("username", name=UserConstraints.USERNAME_UNIQUE.value),
    )

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
