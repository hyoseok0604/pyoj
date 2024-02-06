from typing import Annotated

from fastapi import Depends, Request

from web.models.user import SessionUser
from web.services.session.postgres import PostgresSessionService


async def get_session_user(
    request: Request, session_service: PostgresSessionService
) -> SessionUser | None:
    session_key = request.cookies.get("session")

    if session_key is None:
        return None

    session_data = await session_service.verify_session(session_key)
    return session_data


SessionUserDependency = Annotated[SessionUser | None, Depends(get_session_user)]
