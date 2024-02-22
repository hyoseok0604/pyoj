from celery import Celery
from celery.backends.redis import RedisBackend


def redis_backend_with_database(app: Celery, redis_url: str, db: int) -> RedisBackend:
    url = f"{redis_url[:redis_url.rfind("/")]}/{db}"

    return RedisBackend(app=app, url=url)
