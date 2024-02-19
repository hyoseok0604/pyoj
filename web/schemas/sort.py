from typing import Literal

from web.schemas.base import BaseSchema


class SortSchema(BaseSchema):
    sort: Literal["asc", "desc"] = "desc"
