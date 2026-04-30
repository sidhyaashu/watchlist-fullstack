import json
from typing import Optional, List
from uuid import UUID
import redis.asyncio as redis
from app.core.config import settings

# 🔹 Redis connection
redis_client = redis.from_url(
    getattr(settings, "REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True
)


class WatchlistCache:
    TTL = 3600  # 1 hour

    @staticmethod
    def _get_key(user_id: UUID) -> str:
        return f"user_watchlists:{user_id}"

    @staticmethod
    async def get_watchlists(user_id: UUID) -> Optional[List[dict]]:
        key = WatchlistCache._get_key(user_id)
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def set_watchlists(user_id: UUID, watchlists: List[dict]):
        key = WatchlistCache._get_key(user_id)
        await redis_client.set(
            key,
            json.dumps(watchlists),
            ex=WatchlistCache.TTL
        )

    @staticmethod
    async def invalidate(user_id: UUID):
        key = WatchlistCache._get_key(user_id)
        await redis_client.delete(key)
