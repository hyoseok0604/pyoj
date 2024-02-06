from fastapi import APIRouter, HTTPException, status

from web.core.dependencies import SessionUserDependency
from web.schemas.user import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    GetUserResponseSchema,
)
from web.services.user import UserService

api_router = APIRouter(prefix="/users")


@api_router.post(
    "", response_model=CreateUserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_user_api(schema: CreateUserRequestSchema, service: UserService):
    user = await service.create(schema)

    return user


@api_router.get("/{id}", response_model=GetUserResponseSchema)
async def get_user_api(id: int, service: UserService):
    user = await service.get_user_by_id(id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return user


@api_router.delete("/{id}")
async def delete_user_api(id: int, user: SessionUserDependency, service: UserService):
    deleted_user = await service.delete_user_by_id(id, user)

    return deleted_user
