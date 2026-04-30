import redis.asyncio as aioredis
from app.core.config import settings

# Single shared async Redis client for the entire service.
# decode_responses=True means all values come back as str, not bytes.
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8",
)
