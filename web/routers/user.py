from fastapi import APIRouter, HTTPException, status

from web.schemas.user import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
)
from web.services.user import UserService

api_router = APIRouter(prefix="/users")


@api_router.post("/", response_model=CreateUserResponseSchema)
async def create_user_api(schema: CreateUserRequestSchema, service: UserService):
    user = await service.create(schema)

    return user


@api_router.get("/{id}", response_model=GetUserResponseSchema)
async def get_user_api(id: int, service: UserService):
    user = await service.get_user_by_id(id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user
