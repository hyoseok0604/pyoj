from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypedDict

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session
from starlette.responses import Response

from web.core.database import async_engine, get_async_session
from web.core.migration import migration
from web.core.settings import settings
from web.main import app
from web.models import BaseModel


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(str(settings.postgres_uri))


@pytest.fixture(scope="function")
def dbsession(engine: Engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def empty_metadata() -> MetaData:
    class EmptyBaseModel(DeclarativeBase):
        ...

    return EmptyBaseModel.metadata


@pytest.fixture(scope="session")
def metadata() -> MetaData:
    return BaseModel.metadata


@pytest.fixture(autouse=True)
def monkeypatch_response_set_cookie(monkeypatch):
    original_set_cookie = Response.set_cookie
    Response._set_cookie = original_set_cookie  # type: ignore

    def set_cookie(self, *args, **kwargs):
        del kwargs["secure"]
        self._set_cookie(*args, **kwargs, secure=False)

    monkeypatch.setattr("starlette.responses.Response.set_cookie", set_cookie)

    yield

    delattr(Response, "_set_cookie")


@pytest.fixture(scope="session")
async def savepoint_connection():
    async with async_engine.connect() as connection:
        yield connection


@pytest.fixture(scope="module")
async def life_span_app(savepoint_connection: AsyncConnection):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with savepoint_connection.begin() as transaction:
            async with AsyncSession(bind=savepoint_connection) as session:

                def wrapped_migration(session: Session):
                    migration(session.connection(), BaseModel.metadata)

                await session.run_sync(wrapped_migration)
                await session.commit()

            yield

            await transaction.rollback()

    app.router.lifespan_context = lifespan

    async with LifespanManager(app):
        yield app


@pytest.fixture(scope="function")
async def client(savepoint_connection: AsyncConnection, life_span_app: FastAPI):
    async with savepoint_connection.begin_nested() as nested_transaction:
        async with AsyncSession(
            bind=savepoint_connection, join_transaction_mode="create_savepoint"
        ) as session:

            async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
                yield session

            life_span_app.dependency_overrides[
                get_async_session
            ] = get_test_async_session

            async with AsyncClient(
                app=life_span_app, base_url="http://localhost:8080"
            ) as client:
                yield client

        await nested_transaction.rollback()


@pytest.fixture
async def create_users(request, client):
    try:
        count = request.param.get("count")
    except AttributeError:
        count = 1

    users = [
        {"username": f"username{i}", "password": f"password{i}"} for i in range(count)
    ]

    for user in users:
        response = await client.post(
            "/api/users",
            json={
                "username": user["username"],
                "password1": user["password"],
                "password2": user["password"],
            },
        )

        user.update({"id": response.json().get("id")})

    return users


@pytest.fixture
async def login(client: AsyncClient, create_users):
    async def _login(idx: int):
        assert idx < len(create_users)

        request = await client.post(
            "/api/login",
            json={
                "username": create_users[idx]["username"],
                "password": create_users[idx]["password"],
            },
        )

        assert request.status_code == 204

    return _login


@pytest.fixture
async def logout(client: AsyncClient):
    async def _logout():
        await client.post("/api/logout")

    return _logout


class FixtureProblem(TypedDict):
    id: int
    title: str
    time_limit: int
    memory_limit: int
    description: str
    input_description: str
    output_description: str
    limit_description: str


@pytest.fixture
async def create_problems(request, client, login, logout, create_users):
    try:
        creators = request.param.get("creators")
    except AttributeError:
        return []

    problems: list[FixtureProblem] = [
        {
            "id": -1,
            "title": f"title{i}",
            "time_limit": 1000,
            "memory_limit": 256,
            "description": f"description{i}",
            "input_description": f"input_description{i}",
            "output_description": f"output_description{i}",
            "limit_description": f"limit_description{i}",
        }
        for i in range(len(creators))
    ]

    for problem, creator in zip(problems, creators):
        await login(creator)

        response = await client.post("/api/problems", json=problem)
        problem["id"] = response.json().get("id")

    await logout()

    return problems
