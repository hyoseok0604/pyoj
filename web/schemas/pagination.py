from pydantic import Field, computed_field

from web.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    page: int = Field(1, ge=1)
    count: int = Field(20, ge=1, le=100)

    @computed_field
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.count
