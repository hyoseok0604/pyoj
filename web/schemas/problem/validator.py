from pydantic_core import PydanticCustomError


def validate_time_limit(time_limit: int) -> int:
    if not 1 <= time_limit <= 1000:
        raise PydanticCustomError(
            "time_limit_range", "시간 제한은 1 이상 1000 이하의 정수만 가능합니다."
        )

    return time_limit


def validate_memroy_limit(memory_limit: int) -> int:
    if not 128 <= memory_limit <= 1024:
        raise PydanticCustomError(
            "memory_limit_range",
            "메모리 제한은 128 이상 1024 이하의 정수만 가능합니다.",
        )

    return memory_limit
