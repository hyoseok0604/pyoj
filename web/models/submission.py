from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from judger.compile.result import CompileResult
from judger.execute.result import ExecuteResult
from web.models.base import BaseModel

if TYPE_CHECKING:
    from web.models.language import Language
    from web.models.problem import Problem, Testcase
    from web.models.systemcall import SystemcallCount
    from web.models.user import User


class Submission(BaseModel):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    code: Mapped[str]

    compile_result: Mapped[Optional[CompileResult]] = mapped_column(default=None)
    compile_stdout: Mapped[Optional[str]] = mapped_column(default=None)
    compile_stderr: Mapped[Optional[str]] = mapped_column(default=None)

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

    submission_results: Mapped[list["SubmissionTestcaseResult"]] = relationship(
        back_populates="submission"
    )


class SubmissionTestcaseResult(BaseModel):
    __tablename__ = "submission_testcase_result"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)

    time: Mapped[Optional[int]] = mapped_column(default=None)
    memory: Mapped[Optional[int]] = mapped_column(default=None)

    result: Mapped[Optional[ExecuteResult]] = mapped_column(default=None)

    stdout: Mapped[Optional[str]] = mapped_column(default=None)
    stderr: Mapped[Optional[str]] = mapped_column(default=None)

    submission: Mapped[Submission] = relationship(back_populates="submission_results")
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submission.id", ondelete="CASCADE")
    )

    testcase: Mapped[Optional["Testcase"]] = relationship(
        back_populates="submission_results"
    )
    testcase_id: Mapped[int | None] = mapped_column(
        ForeignKey("testcase.id", ondelete="SET NULL")
    )

    systemcall_counts: Mapped[list["SystemcallCount"]] = relationship(
        back_populates="submission_result"
    )
