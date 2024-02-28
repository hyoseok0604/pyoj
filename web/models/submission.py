from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.language import Language
    from web.models.problem import Problem
    from web.models.systemcall import SystemcallCount
    from web.models.user import User


class Submission(BaseModel):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    code: Mapped[str]

    creator: Mapped[Optional["User"]] = relationship(
        back_populates="submissions", passive_deletes=True
    )
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )

    language: Mapped["Language"] = relationship(back_populates="submissions")
    language_id: Mapped[int] = mapped_column(ForeignKey("language.id"))

    problem: Mapped[Optional["Problem"]] = relationship(back_populates="submissions")
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )

    systemcall_counts: Mapped[list["SystemcallCount"]] = relationship(
        back_populates="submission"
    )
