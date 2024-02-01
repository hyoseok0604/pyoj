from typing import Annotated

from fastapi import Depends, Request

from web.schemas.auth import SessionUser
from web.services.auth import AuthService


async def get_session_user(
    request: Request, auth_service: AuthService
) -> SessionUser | None:
    session_key = request.cookies.get("session")

    if session_key is None:
        return None

    session_data = await auth_service.verify_session(session_key)
    return session_data


SessionUserDependency = Annotated[SessionUser | None, Depends(get_session_user)]
