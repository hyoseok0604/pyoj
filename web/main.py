from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from uvicorn.config import LOGGING_CONFIG

from web.core import settings
from web.core.startup import startup_functions
from web.routers.auth import api_router as auth_api_router
from web.routers.language import api_router as language_api_router
from web.routers.problem import api_router as problem_api_router
from web.routers.submission import api_router as submission_api_router
from web.routers.systemcall import api_router as systemcall_api_router
from web.routers.user import api_router as user_api_router
from web.services.exceptions import (
    AuthException,
    FileTooLargeException,
    InternalServerException,
    NotFoundException,
    PermissionException,
    ServiceException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for startup_function in startup_functions:
        await startup_function(app)

    yield


app = FastAPI(lifespan=lifespan)

view_router = APIRouter()

api_router = APIRouter(prefix="/api")

api_routers: list[APIRouter] = [
    user_api_router,
    auth_api_router,
    problem_api_router,
    systemcall_api_router,
    language_api_router,
    submission_api_router,
]

for router in api_routers:
    api_router.include_router(router)

app.include_router(view_router)
app.include_router(api_router)


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exception: ServiceException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    if isinstance(exception, AuthException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exception, PermissionException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exception, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, InternalServerException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exception, FileTooLargeException):
        status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    return JSONResponse(exception.messages, status_code=status_code)


@app.get("/")
def index():
    return {"Hello": "World"}


if __name__ == "__main__":
    new_logging_config = LOGGING_CONFIG

    new_logging_config["loggers"].update(
        {"web": {"handlers": ["default"], "level": "INFO", "propagate": False}}
    )

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.env == "development",
        log_config=new_logging_config,
    )  # type: ignore
