from web.schemas.base import BaseSchema


class LoginRequestSchema(BaseSchema):
    username: str
    password: str
