# For tasks
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from judger.utils.system_call import Systemcall as JudgerSystemcall
from judger.utils.system_call import parse_systemcall_x86_64_linux_gnu
from web.models.systemcall import Systemcall as DatabaseSystemcall
from web.models.systemcall import SystemcallGroup
from worker.database import DatabaseSession

_log = logging.getLogger()


def parse_systemcalls():
    parsed_systemcalls = parse_systemcall_x86_64_linux_gnu()

    _log.info(f"{len(parsed_systemcalls)} Systemcalls.")

    with DatabaseSession() as session:
        enabled_systemcall_group = _get_enabled_systemcall_group(session)

        if enabled_systemcall_group is None or not _is_same_systemcalls(
            enabled_systemcall_group.systemcalls, parsed_systemcalls
        ):
            _log.info("New systemcall parsed, save systemcall group.")
            _create_systemcall_group(
                session, parsed_systemcalls, enabled_systemcall_group
            )
        else:
            _log.info("Same systemcall parsed, not save.")


def _get_enabled_systemcall_group(session: Session) -> SystemcallGroup | None:
    enabled_systemcall_group_stmt = (
        select(SystemcallGroup)
        .where(SystemcallGroup.is_enabled.is_(True))
        .with_for_update()
    )
    return session.scalar(enabled_systemcall_group_stmt)


def _create_systemcall_group(
    session: Session,
    judger_systemcalls: list[JudgerSystemcall],
    enabled_systemcall_group: SystemcallGroup | None,
):
    systemcalls = [
        DatabaseSystemcall(name=systemcall["name"], number=systemcall["number"])
        for systemcall in judger_systemcalls
    ]

    systemcall_group = SystemcallGroup()
    systemcall_group.systemcalls = systemcalls
    systemcall_group.is_enabled = True

    if enabled_systemcall_group is not None:
        enabled_systemcall_group.is_enabled = False
        session.merge(enabled_systemcall_group)

    session.add(systemcall_group)
    session.commit()


def _is_same_systemcalls(
    original_systemcalls: list[DatabaseSystemcall],
    new_systemcalls: list[JudgerSystemcall],
):
    if len(original_systemcalls) != len(new_systemcalls):
        return False

    sorted_original_systemcalls = sorted(
        original_systemcalls, key=lambda systemcall: systemcall.number
    )
    sorted_new_systemcalls = sorted(
        new_systemcalls, key=lambda systemcall: systemcall["number"]
    )

    for original_systmecall, new_systemcall in zip(
        sorted_original_systemcalls, sorted_new_systemcalls
    ):
        if original_systmecall.number != new_systemcall["number"]:
            return False

        if original_systmecall.name != new_systemcall["name"]:
            return False

    return True
