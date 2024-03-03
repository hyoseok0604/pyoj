from pydantic_core import PydanticCustomError


def validate_code(code: str) -> str:
    if len(code) > 50000:
        raise PydanticCustomError("code_length", "코드는 50000자를 넘길 수 없습니다.")
    return code
