from typing import Never, Sequence, TypeGuard, cast, get_args

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
from sqlalchemy import Connection, Enum, MetaData

from web.logger import _log

EnumOp = CreateEnumOp | DropEnumOp | SyncEnumValuesOp


def is_latest(connection: Connection, metadata: MetaData) -> bool:
    migration_context = MigrationContext.configure(connection, opts={"fn": _nothing})
    migration_script = produce_migrations(context=migration_context, metadata=metadata)
    upgrade_ops = migration_script.upgrade_ops

    if upgrade_ops is None:
        return False

    return len(upgrade_ops.ops) == 0


def migration(connection: Connection, metadata: MetaData):
    migration_context = MigrationContext.configure(connection, opts={"fn": _nothing})
    migration_script = produce_migrations(context=migration_context, metadata=metadata)
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
    if isinstance(op, CreateEnumOp):
        if op.schema != migration_context.dialect.default_schema_name:
            enum = Enum(*op.enum_values, name=op.name, schema=op.schema)
        else:
            enum = Enum(*op.enum_values, name=op.name)
        enum.create(ops.get_bind())
    elif isinstance(op, DropEnumOp):
        if op.schema != migration_context.dialect.default_schema_name:
            enum = Enum(*op.enum_values, name=op.name, schema=op.schema)
        else:
            enum = Enum(*op.enum_values, name=op.name)
        enum.drop(ops.get_bind())
    elif isinstance(op, SyncEnumValuesOp):
        ops.invoke(op)
    else:
        nv: Never = op  # noqa: F841


def _nothing(rev, context):
    return []
