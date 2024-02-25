from fastapi import APIRouter, HTTPException, Query, Response, status

from web.schemas.systemcall import (
    GetSystemcallGroupResponseSchema,
    GetSystemcallGroupsRequestSchema,
    GetSystemcallGroupsResponseSchema,
)
from web.services.systemcall import SystemcallService
from web.services.task import TaskService

api_router = APIRouter(prefix="/systemcall-groups")


@api_router.post("", status_code=status.HTTP_202_ACCEPTED, response_class=Response)
async def create_systemcall_group_api(task_service: TaskService):
    task_service.request_parse_systemcall_task()


@api_router.get("", response_model=list[GetSystemcallGroupsResponseSchema])
async def get_systemcall_groups_api(
    systemcall_service: SystemcallService,
    page: int = Query(default=1, ge=1),
    count: int = Query(default=20, ge=1, le=100),
):
    schema = GetSystemcallGroupsRequestSchema(page=page, count=count)
    systemcall_groups = await systemcall_service.get_systemcall_groups(schema)

    return [
        {**systemcall_group.__dict__, "count": count}
        for systemcall_group, count in systemcall_groups
    ]


@api_router.get("/enabled", response_model=GetSystemcallGroupResponseSchema)
async def get_enabled_systemcall_group_api(systemcall_service: SystemcallService):
    systemcall_group = await systemcall_service.get_enabled_systemcall_group()

    if systemcall_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return systemcall_group


@api_router.get("/{id}", response_model=GetSystemcallGroupResponseSchema)
async def get_systemcall_group_api(id: int, systemcall_service: SystemcallService):
    systemcall_group = await systemcall_service.get_systemcall_group(id)

    if systemcall_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return systemcall_group
