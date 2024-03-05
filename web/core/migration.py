from typing import Sequence, TypeGuard, cast, get_args

import alembic_postgresql_enum  # noqa: F401
from alembic.autogenerate import produce_migrations
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.operations.ops import MigrateOperation, OpContainer
from alembic_postgresql_enum.operations import (
    CreateEnumOp,
    DropEnumOp,
    SyncEnumValuesOp,
)
from sqlalchemy import Connection, MetaData, create_engine
from sqlalchemy.orm import Session

from web.core.settings import settings
from web.logger import DisableSqlalchemyLogger, _log
from web.models import (
    BaseModel,
    Language,
    LanguageSystemcallCountLimit,
    Problem,
    SessionUser,
    Submission,
    SubmissionTestcaseResult,
    Systemcall,
    SystemcallCount,
    SystemcallGroup,
    Testcase,
    User,
)

EnumOp = CreateEnumOp | DropEnumOp | SyncEnumValuesOp


def migration(connection: Connection, metadata: MetaData):
    with DisableSqlalchemyLogger():
        migration_context = MigrationContext.configure(
            connection,
            opts={
                "fn": _nothing,
                "include_schemas": False,
                "compare_server_default": True,
            },
        )
        migration_script = produce_migrations(
            context=migration_context, metadata=metadata
        )
        upgrade_ops = migration_script.upgrade_ops

        if upgrade_ops is None:
            _log.info("Upgrade Operations is None.")
            return

        ops = Operations(migration_context=migration_context)

    count = _run_operations_recursive(migration_context, ops, upgrade_ops.ops)

    _log.info(f"Run {count} Operations for migration.")


def _is_op_container(op: MigrateOperation) -> TypeGuard[OpContainer]:
    return issubclass(type(op), OpContainer)


def _run_operations_recursive(
    migration_context: MigrationContext,
    ops: Operations,
    migrate_operations: Sequence[MigrateOperation],
) -> int:
    count = 0
    for op in migrate_operations:
        if _is_op_container(op):
            count += _run_operations_recursive(migration_context, ops, op.ops)
        else:
            if isinstance(op, get_args(EnumOp)):
                op = cast(EnumOp, op)
                _run_enum_operations(migration_context, ops, op)
            else:
                ops.invoke(op)
            count += 1
    return count


def _run_enum_operations(
    migration_context: MigrationContext, ops: Operations, op: EnumOp
):
    # if isinstance(op, CreateEnumOp):
    #     if op.schema != migration_context.dialect.default_schema_name:
    #         enum = Enum(*op.enum_values, name=op.name, schema=op.schema)
    #     else:
    #         enum = Enum(*op.enum_values, name=op.name)
    #     enum.create(ops.get_bind())
    # elif isinstance(op, DropEnumOp):
    #     if op.schema != migration_context.dialect.default_schema_name:
    #         enum = Enum(*op.enum_values, name=op.name, schema=op.schema)
    #     else:
    #         enum = Enum(*op.enum_values, name=op.name)
    #     enum.drop(ops.get_bind())
    # elif isinstance(op, SyncEnumValuesOp):
    #     ops.sync_enum_values(  # type: ignore[reportAttributeAccessIssue]
    #         op.schema,
    #         op.name,
    #         op.new_values,
    #         op.affected_columns,
    #         enum_values_to_rename=[],
    #     )
    # else:
    #     nv: Never = op  # noqa: F841
    ...


def _nothing(rev, context):
    return []


if __name__ == "__main__":
    engine = create_engine(str(settings.postgres_uri))
    connection = Connection(engine=engine)
    session = Session(connection)
    migration(connection, BaseModel.metadata)

    user = User()
    user.username = "test"
    user.password = "test"
    session.add(user)

    session_user = SessionUser()
    session_user.session_key = "key"
    session_user.user = user
    session.add(session_user)

    problem = Problem()
    problem.title = "title"
    problem.description = ""
    problem.input_description = ""
    problem.output_description = ""
    problem.limit_description = ""
    problem.creator = user
    session.add(problem)

    testcase = Testcase()
    testcase.input_preview = "in"
    testcase.output_preview = "out"
    testcase.input_size = 1
    testcase.output_size = 1
    testcase.original_input_filename = "in"
    testcase.original_output_filename = "out"
    testcase.problem = problem
    session.add(testcase)

    language = Language()
    language.display_name = "lang"
    language.filename = "a.a"
    language.compile_command = "command"
    language.execute_command = "command"
    session.add(language)

    systemcall_group = SystemcallGroup()
    session.add(systemcall_group)

    systemcall = Systemcall()
    systemcall.name = "systemcall"
    systemcall.number = 1
    systemcall.systemcall_group = systemcall_group
    session.add(systemcall)

    language_systemcall_count_limit = LanguageSystemcallCountLimit()
    language_systemcall_count_limit.language = language
    language_systemcall_count_limit.systemcall = systemcall
    language_systemcall_count_limit.count = 11
    session.add(language_systemcall_count_limit)

    submission = Submission()
    submission.code = "code"
    submission.creator = user
    submission.language = language
    submission.problem = problem
    session.add(submission)

    submission_testcase_result = SubmissionTestcaseResult()
    submission_testcase_result.submission = submission
    submission_testcase_result.testcase = testcase
    session.add(submission_testcase_result)

    systemcall_count = SystemcallCount()
    systemcall_count.count = 11
    systemcall_count.systemcall = systemcall
    systemcall_count.submission_result = submission_testcase_result
    session.add(systemcall_count)

    session.commit()
