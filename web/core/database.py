from typing import Annotated, AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from web.core.settings import settings

async_engine = create_async_engine(
    str(settings.postgres_uri),
    echo=True,
    connect_args={"application_name": "sqlalchemy"},
)


async_session = async_sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]


redis_pool = redis.ConnectionPool.from_url(str(settings.redis_uri))


async def get_redis():
    async with redis.Redis(connection_pool=redis_pool) as connection:
        yield connection


AsyncRedisDependency = Annotated[redis.Redis, Depends(get_redis)]
