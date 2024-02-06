from fastapi import APIRouter, HTTPException, Request, Response, status

from web.core.dependencies import SessionUserDependency
from web.logger import _log
from web.schemas.auth import LoginRequestSchema
from web.services.auth import AuthService

api_router = APIRouter()


@api_router.post("/login")
async def login_api(schema: LoginRequestSchema, service: AuthService):
    session_key = await service.login(schema)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    response.set_cookie(
        "session",
        session_key,
        max_age=int(service.session_service.session_timeout.total_seconds()),
        secure=True,
        httponly=True,
    )

    return response


@api_router.post("/logout")
async def logout_api(request: Request, service: AuthService):
    session_key = request.cookies.get("session")

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    if session_key is None:
        return response

    is_success = await service.logout(session_key)
    if not is_success:
        _log.warn("Session data was not deleted correctly.")

    response.delete_cookie("session")

    return response


@api_router.get("/me")
async def me_api(session_user: SessionUserDependency):
    if session_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return session_user.user
