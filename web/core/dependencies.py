from fastapi import Request

from web.services.auth import AuthService


async def set_user_state_dependency(request: Request, auth_service: AuthService):
    session_key = request.cookies.get("session")

    if session_key is None:
        request.state.user = None
        return

    session_data = await auth_service.verify_session(session_key)
    request.state.user = session_data
