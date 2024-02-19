from typing import Annotated

from pydantic import AfterValidator, Field

from web.schemas.problem.validator import validate_memroy_limit, validate_time_limit

TimeLimit = Annotated[int, Field(default=1000), AfterValidator(validate_time_limit)]
MemoryLimit = Annotated[int, Field(default=256), AfterValidator(validate_memroy_limit)]
Description = str
