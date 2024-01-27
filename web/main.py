from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uvicorn.config import LOGGING_CONFIG

from web.core import settings
from web.core.database import async_session
from web.core.dependencies import set_user_state_dependency
from web.core.migration import migration
from web.models.base import BaseModel
from web.routers.auth import api_router as auth_api_router
from web.routers.user import api_router as user_api_router
from web.services.exception import ServiceException


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:

        def wrapped_migration(session: Session):
            migration(session.connection(), BaseModel.metadata)

        await session.run_sync(wrapped_migration)
        await session.commit()

    yield


app = FastAPI(lifespan=lifespan)

view_router = APIRouter()

api_router = APIRouter(dependencies=[Depends(set_user_state_dependency)])

api_router.include_router(user_api_router)
api_router.include_router(auth_api_router)

app.include_router(view_router)
app.include_router(api_router)


@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exception: ServiceException):
    return JSONResponse(
        exception.messages, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


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
