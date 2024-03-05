from typing import Annotated

from pydantic import Field, computed_field

from web.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    page: Annotated[int, Field(default=1, ge=1)] = 1
    count: Annotated[int, Field(default=20, ge=10, le=40)] = 20

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.count
