import pytest
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from web.core.settings import settings
from web.models import BaseModel


@pytest.fixture(scope="session")
def engine() -> Engine:
    return create_engine(str(settings.postgres_uri))


@pytest.fixture(scope="function")
def dbsession(engine: Engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

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
