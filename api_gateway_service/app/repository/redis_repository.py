import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def increment(key: str, expire: int = 60):
    current = await redis_client.incr(key)

    if current == 1:
        await redis_client.expire(key, expire)

    return current


async def get_ttl(key: str):
    return await redis_client.ttl(key)