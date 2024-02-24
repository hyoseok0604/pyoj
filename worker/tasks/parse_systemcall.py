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

        if enabled_systemcall_group is None:
            _log.info("Create new systemcall group with enable.")
            _create_systemcall_group(session, parsed_systemcalls, True)
        elif not _is_same_systemcalls(
            enabled_systemcall_group.systemcalls, parsed_systemcalls
        ):
            _log.info(
                "New systemcall parsed. Create new systemcall group without enable."
            )
            _create_systemcall_group(session, parsed_systemcalls, False)
        else:
            _log.info("Same systemcall parsed. Not save.")


def _get_enabled_systemcall_group(session: Session) -> SystemcallGroup | None:
    enabled_systemcall_group_stmt = select(SystemcallGroup).where(
        SystemcallGroup.is_enabled.is_(True)
    )
    return session.scalar(enabled_systemcall_group_stmt)


def _create_systemcall_group(
    session: Session,
    judger_systemcalls: list[JudgerSystemcall],
    enabled: bool,
):
    systemcalls = [
        DatabaseSystemcall(name=systemcall["name"], number=systemcall["number"])
        for systemcall in judger_systemcalls
    ]

    systemcall_group = SystemcallGroup()
    systemcall_group.systemcalls = systemcalls
    systemcall_group.is_enabled = enabled

    session.add(systemcall_group)
    session.commit()


def _is_same_systemcalls(orig: list[DatabaseSystemcall], new: list[JudgerSystemcall]):
    orig_index = 0
    new_index = 0

    sorted_orig = sorted(orig, key=lambda systemcall: systemcall.number)
    sorted_new = sorted(new, key=lambda systemcall: systemcall["number"])

    while orig_index < len(orig) and new_index < len(new):
        if sorted_orig[orig_index].number < sorted_new[new_index]["number"]:
            orig_index += 1
            continue
        if sorted_orig[orig_index].number > sorted_new[new_index]["number"]:
            new_index += 1
            continue

        if sorted_orig[orig_index].name != sorted_new[new_index]["name"]:
            return False

        orig_index += 1
        new_index += 1

    return orig_index == len(orig) and new_index == len(new)
