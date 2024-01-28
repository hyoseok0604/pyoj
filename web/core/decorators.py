from typing import Annotated, Type, TypeVar, cast

from fastapi import Depends

T = TypeVar("T")


def as_annotated_dependency(cls: Type[T]) -> Type[T]:
    return cast(Type[T], Annotated[cls, Depends(cls)])
