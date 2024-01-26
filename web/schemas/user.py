import string
from datetime import datetime
from typing import Self

import bcrypt
from pydantic import SecretStr, field_validator, model_validator
from pydantic_core import PydanticCustomError

from web.models.user import User
from web.schemas import SerializeToModel
from web.schemas.base import BaseSchema


class CreateUserRequestSchema(SerializeToModel[User], BaseSchema):
    username: str
    password1: SecretStr
    password2: SecretStr

    def serialize(self):
        user = User()

        user.username = self.username

        salt = bcrypt.gensalt()
        user.password = bcrypt.hashpw(
            self.password1.get_secret_value().encode(), salt
        ).decode()

        return user

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        if not 6 <= len(username) <= 24:
            raise PydanticCustomError(
                "username_length",
                "아이디는 6자 이상 24자 이하의 문자열만 가능합니다.",
            )

        alphanumeric = string.ascii_letters + string.digits
        if not all(c in alphanumeric for c in username):
            raise PydanticCustomError(
                "username_not_alphanumeric",
                "아이디는 영어 대소문자, 숫자만 가능합니다.",
            )

        return username

    @field_validator("password1")
    @classmethod
    def validate_password1(cls, password1: SecretStr) -> SecretStr:
        if not 6 <= len(password1) <= 24:
            raise PydanticCustomError(
                "password_length", "비밀번호 길이는 6 이상 24 이하여야 합니다."
            )

        printable = string.ascii_letters + string.digits + string.punctuation
        if not all(c in printable for c in password1.get_secret_value()):
            raise PydanticCustomError(
                "password_not_printable",
                "비밀번호는 영어 대소문자, 숫자 특수문자만 가능합니다.",
            )

        return password1

    @model_validator(mode="after")
    def validate_password_match(self) -> Self:
        if (
            self.password1 is not None
            and self.password2 is not None
            and self.password1 != self.password2
        ):
            raise PydanticCustomError(
                "password_not_match", "비밀번호가 일치하지 않습니다."
            )

        return self


class CreateUserResponseSchema(BaseSchema):
    id: int
    username: str
    created_at: datetime


class GetUserRequestSchema(BaseSchema):
    username: str


class GetUserResponseSchema(BaseSchema):
    id: int
    username: str
    created_at: datetime
