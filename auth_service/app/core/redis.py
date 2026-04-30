import redis.asyncio as redis
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._redis = None

    async def connect(self):
        if not self._redis:
            try:
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                await self._redis.ping()
                logger.info("Connection established with Redis cluster")
            except Exception as e:
                logger.error(f"Redis initialization failed: {e}")
                self._redis = None

    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis connection closed")

    async def get_client(self):
        if not self._redis:
            await self.connect()
        return self._redis

# Singleton instance
redis_client = RedisClient()

async def get_redis():
    """Dependency for injecting Redis client into FastAPI routes."""
    return await redis_client.get_client()
