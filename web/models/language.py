from typing import TYPE_CHECKING

from sqlalchemy import sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.submission import Submission


class Language(BaseModel):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    display_name: Mapped[str] = mapped_column(unique=True)
    filename: Mapped[str]
    compile_command: Mapped[str]
    execute_command: Mapped[str]
    is_enabled: Mapped[bool] = mapped_column(server_default=sql.true())

    submissions: Mapped[list["Submission"]] = relationship(back_populates="language")
