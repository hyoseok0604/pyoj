from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

USERNAME_UNIQUE_CONSTRAINT_NAME = "user_username_unique"
SESEEION_KEY_UNIQUE_CONSTRAINT_NAME = "session_user_session_key_unique"


class User(BaseModel):
    __tablename__ = "user"

    __table_args__ = (
        UniqueConstraint("username", name=USERNAME_UNIQUE_CONSTRAINT_NAME),
    )

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str]
    password: Mapped[str] = mapped_column(deferred=True)


class SessionUser(BaseModel):
    __tablename__ = "session_user"

    __table_args__ = (
        UniqueConstraint("session_key", name=SESEEION_KEY_UNIQUE_CONSTRAINT_NAME),
    )

    session_key: Mapped[str] = mapped_column(primary_key=True)

    user: Mapped[User] = relationship()
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
