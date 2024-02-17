from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, sql, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.user import User


class Problem(BaseModel):
    __tablename__ = "problem"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str]

    time_limit: Mapped[int] = mapped_column(server_default=text("1000"))
    memory_limit: Mapped[int] = mapped_column(server_default=text("512"))

    is_public: Mapped[bool] = mapped_column(server_default=sql.false())

    description: Mapped[str] = mapped_column(deferred_group="problem_descriptions")
    input_description: Mapped[str] = mapped_column(
        deferred_group="problem_descriptions"
    )
    output_description: Mapped[str] = mapped_column(
        deferred_group="problem_descriptions"
    )
    limit_description: Mapped[str] = mapped_column(
        deferred_group="problem_descriptions"
    )

    testcases: Mapped[list["Testcase"]] = relationship(
        back_populates="problem", passive_deletes=True
    )

    creator: Mapped["User"] = relationship(back_populates="problems")
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )


class Testcase(BaseModel):
    __tablename__ = "testcase"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    original_input_filename: Mapped[str]
    original_output_filename: Mapped[str]
    input_preview: Mapped[str] = mapped_column(server_default="")
    output_preview: Mapped[str] = mapped_column(server_default="")
    input_size: Mapped[int] = mapped_column(server_default="0")
    output_size: Mapped[int] = mapped_column(server_default="0")

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problem.id", ondelete="CASCADE")
    )
    problem: Mapped["Problem"] = relationship(back_populates="testcases")
