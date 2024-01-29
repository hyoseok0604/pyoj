from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from pydantic import BaseModel as Schema
from pydantic import ConfigDict, model_serializer

from web.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseSchema(Schema):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SerializeToModelSchema(BaseSchema, Generic[T]):
    @model_serializer
    def serialize(self) -> T:
        ...

    if TYPE_CHECKING:

        def model_dump(  # type: ignore[reportIncompatibleMethodOverride]
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
        ) -> T:
            ...
