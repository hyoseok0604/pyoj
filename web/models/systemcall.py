from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, PrimaryKeyConstraint, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.submission import SubmissionTestcaseResult


class Systemcall(BaseModel):
    __tablename__ = "systemcall"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str]
    number: Mapped[int]

    systemcall_group_id: Mapped[int] = mapped_column(ForeignKey("systemcall_group.id"))
    systemcall_group: Mapped["SystemcallGroup"] = relationship(
        back_populates="systemcalls"
    )

    systemcall_counts: Mapped[list["SystemcallCount"]] = relationship(
        back_populates="systemcall"
    )


class SystemcallCount(BaseModel):
    __tablename__ = "systemcall_count"

    count: Mapped[int]

    systemcall_id: Mapped[int] = mapped_column(
        ForeignKey("systemcall.id"), primary_key=True
    )
    systemcall: Mapped[Systemcall] = relationship(back_populates="systemcall_counts")

    submission_result_id: Mapped[int] = mapped_column(
        ForeignKey("submission_testcase_result.id"), primary_key=True
    )
    submission_result: Mapped["SubmissionTestcaseResult"] = relationship(
        back_populates="systemcall_counts"
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            systemcall_id, submission_result_id, name="systemcall_count_pkey"
        ),
    )


class SystemcallGroup(BaseModel):
    __tablename__ = "systemcall_group"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(server_default=sql.false())

    systemcalls: Mapped[list[Systemcall]] = relationship(
        back_populates="systemcall_group"
    )

    __table_args__ = (
        Index(
            "unique_enabled_systemcall_group",
            is_enabled,
            unique=True,
            postgresql_where=is_enabled.is_(True),
        ),
    )
