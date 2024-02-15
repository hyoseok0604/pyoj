from typing import Annotated

from pydantic import Field, computed_field

from web.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    page: Annotated[int, Field(ge=1)] = 1
    count: Annotated[int, Field(ge=1, le=100)] = 20

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.count
