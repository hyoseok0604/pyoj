from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from pydantic import model_serializer

from web.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class SerializeToModel(Generic[T], ABC):
    @abstractmethod
    @model_serializer
    def serialize(self) -> T:
        ...

    if TYPE_CHECKING:

        def model_dump(
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
