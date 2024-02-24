from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from worker.settings import settings

engine = create_engine(str(settings.postgres_uri), poolclass=NullPool)

DatabaseSession = sessionmaker(engine, autoflush=False, expire_on_commit=False)
