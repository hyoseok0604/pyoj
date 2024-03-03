import inspect
from copy import copy
from itertools import chain
from typing import (
    Any,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    Type,
    TypeVar,
)

from fastapi.params import Param, ParamTypes
from pydantic.fields import FieldInfo

from web.schemas.base import BaseSchema

T = TypeVar("T", bound=BaseSchema)
F = TypeVar("F", bound=Callable[..., Any])
P = ParamSpec("P")
R = TypeVar("R")


class QueryLike(Param):
    in_ = ParamTypes.query


def copy_slots(original: FieldInfo, new: FieldInfo):
    slots = chain.from_iterable(
        getattr(s, "__slots__", []) for s in original.__class__.__mro__
    )

    for var in slots:
        setattr(new, var, copy(getattr(original, var)))


def InjectRequestSchemaToQuery(schema_cls: Type[T]):
    def decorator(
        func: Callable[Concatenate[T, P], R],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())[1:]

        for fieldname, info in schema_cls.model_fields.items():
            query = QueryLike()

            copy_slots(info, query)

            new_parameter = inspect.Parameter(
                name=fieldname,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=query,
                annotation=info.annotation,
            )

            parameters.append(new_parameter)

        async def new_function(*args: P.args, **kwargs: P.kwargs) -> R:
            schema_args = {}
            new_kwargs = copy(kwargs)
            for k, v in kwargs.items():
                if k in schema_cls.model_fields.keys():
                    schema_args[k] = v
                    del new_kwargs[k]

            schema = schema_cls(**schema_args)

            if inspect.iscoroutinefunction(func):
                return await func(schema, *args, **new_kwargs)
            else:
                return func(schema, *args, **new_kwargs)

        new_function.__signature__ = inspect.Signature(  # type: ignore
            parameters, return_annotation=sig.return_annotation
        )

        return new_function

    return decorator
