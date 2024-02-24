from typing import Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from web.core.database import AsyncSessionDependency
from web.core.decorators import as_annotated_dependency
from web.models.systemcall import SystemcallGroup
from web.schemas.systemcall import GetSystemcallGroupsRequestSchema


@as_annotated_dependency
class SystemcallService:
    def __init__(self, session: AsyncSessionDependency) -> None:
        self.session = session

    async def get_systemcall_groups(
        self, schema: GetSystemcallGroupsRequestSchema
    ) -> Sequence[Tuple[SystemcallGroup, int]]:
        stmt = (
            select(SystemcallGroup, func.count(SystemcallGroup.id).label("count"))
            .limit(schema.count)
            .offset(schema.offset)
            .join(SystemcallGroup.systemcalls)
            .group_by(SystemcallGroup.id)
            .order_by(SystemcallGroup.id.desc())
        )

        systemcall_groups_with_count = (await self.session.execute(stmt)).tuples().all()

        return systemcall_groups_with_count

    async def get_enabled_systemcall_group(self) -> SystemcallGroup | None:
        stmt = (
            select(SystemcallGroup)
            .where(SystemcallGroup.is_enabled.is_(True))
            .options(selectinload(SystemcallGroup.systemcalls))
        )

        systemcall_group = await self.session.scalar(stmt)

        return systemcall_group

    async def get_systemcall_group(self, id: int) -> SystemcallGroup | None:
        stmt = (
            select(SystemcallGroup)
            .where(SystemcallGroup.id == id)
            .options(selectinload(SystemcallGroup.systemcalls))
        )

        systemcall_group = await self.session.scalar(stmt)

        return systemcall_group
