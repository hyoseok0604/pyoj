import uvicorn
from fastapi import APIRouter, FastAPI
from uvicorn.config import LOGGING_CONFIG

from web.core import settings

app = FastAPI()

view_router = APIRouter()

api_router = APIRouter()

app.include_router(view_router)
app.include_router(api_router)


@app.get("/")
def index():
    return {"Hello": "World!!!....!#!@#!@"}


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
