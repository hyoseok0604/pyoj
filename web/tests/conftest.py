from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

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


@pytest.fixture(scope="session")
async def savepoint_connection():
    async with async_engine.connect() as connection:
        yield connection


@pytest.fixture(scope="session")
async def client(savepoint_connection: AsyncConnection):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with savepoint_connection.begin() as transaction:
            async with AsyncSession(
                bind=savepoint_connection, join_transaction_mode="create_savepoint"
            ) as session:

                def wrapped_migration(session: Session):
                    migration(session.connection(), BaseModel.metadata)

                await session.run_sync(wrapped_migration)
                await session.commit()

            yield

            await transaction.rollback()

    async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with savepoint_connection.begin_nested() as transaction:
            async with AsyncSession(
                bind=savepoint_connection, join_transaction_mode="create_savepoint"
            ) as session:
                yield session

            await transaction.rollback()

    app.dependency_overrides[get_async_session] = get_test_async_session

    app.router.lifespan_context = lifespan

    async with LifespanManager(app), AsyncClient(
        app=app, base_url="http://localhost:8080"
    ) as client:
        yield client
