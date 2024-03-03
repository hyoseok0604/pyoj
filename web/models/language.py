from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.submission import Submission
    from web.models.systemcall import Systemcall


class Language(BaseModel):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    display_name: Mapped[str] = mapped_column(unique=True)
    filename: Mapped[str]
    compile_command: Mapped[str]
    execute_command: Mapped[str]
    is_enabled: Mapped[bool] = mapped_column(server_default=sql.true())

    submissions: Mapped[list["Submission"]] = relationship(back_populates="language")

    systemcall_count_limits: Mapped[
        list["LanguageSystemcallCountLimit"]
    ] = relationship(back_populates="language")


class LanguageSystemcallCountLimit(BaseModel):
    __tablename__ = "language_sysemcall_policy"

    language_id: Mapped[int] = mapped_column(
        ForeignKey("language.id"), primary_key=True
    )
    language: Mapped[Language] = relationship(back_populates="systemcall_count_limits")

    systemcall_id: Mapped[int] = mapped_column(
        ForeignKey("systemcall.id"), primary_key=True
    )
    systemcall: Mapped["Systemcall"] = relationship()

    count: Mapped[int]
