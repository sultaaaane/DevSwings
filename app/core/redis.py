from redis import Redis, ConnectionPool
from app.config import settings


pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=10,
    decode_responses=True
)


def get_redis():
    client = Redis(connection_pool=pool)
    try:
        yield client
    finally:
        client.close()