from datetime import datetime

from web.schemas.base import BaseSchema
from web.schemas.pagination import PaginationSchema


class Systemcall(BaseSchema):
    id: int
    name: str
    number: int


class GetSystemcallGroupsRequestSchema(PaginationSchema):
    ...


class GetSystemcallGroupsResponseSchema(BaseSchema):
    id: int
    is_enabled: bool
    count: int
    created_at: datetime


class GetSystemcallGroupResponseSchema(BaseSchema):
    id: int
    is_enabled: bool
    systemcalls: list[Systemcall]
    created_at: datetime
