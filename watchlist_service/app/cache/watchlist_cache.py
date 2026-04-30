import json
from typing import Optional
from uuid import UUID

from app.cache.redis_client import redis_client
from app.utils.logger import logger


class WatchlistCache:
    # Separate TTLs for different access patterns
    LIST_TTL = 300    # 5 min — list changes on create/delete
    DETAIL_TTL = 600  # 10 min — single watchlist changes rarely

    @staticmethod
    def _list_key(user_id: UUID, skip: int, limit: int) -> str:
        # Pagination-aware key: each page is cached independently
        return f"watchlists:{user_id}:{skip}:{limit}"

    @staticmethod
    def _detail_key(watchlist_id: UUID) -> str:
        return f"watchlist:{watchlist_id}"

    # ─── List ──────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_list(user_id: UUID, skip: int, limit: int) -> Optional[list[dict]]:
        key = WatchlistCache._list_key(user_id, skip, limit)
        data = await redis_client.get(key)
        if data is not None:
            logger.debug(f"[cache:hit] {key}")
            return json.loads(data)
        logger.debug(f"[cache:miss] {key}")
        return None

    @staticmethod
    async def set_list(user_id: UUID, skip: int, limit: int, watchlists: list[dict]):
        key = WatchlistCache._list_key(user_id, skip, limit)
        await redis_client.set(key, json.dumps(watchlists, default=str), ex=WatchlistCache.LIST_TTL)

    @staticmethod
    async def invalidate_list(user_id: UUID):
        """
        Scan and delete all paginated list keys for this user.
        Pattern: watchlists:{user_id}:*
        Using SCAN to avoid blocking Redis with KEYS in production.
        """
        pattern = f"watchlists:{user_id}:*"
        async for key in redis_client.scan_iter(match=pattern, count=100):
            await redis_client.delete(key)
        logger.debug(f"[cache:invalidate] pattern={pattern}")

    # ─── Single Watchlist ──────────────────────────────────────────────────────

    @staticmethod
    async def get_detail(watchlist_id: UUID) -> Optional[dict]:
        key = WatchlistCache._detail_key(watchlist_id)
        data = await redis_client.get(key)
        if data is not None:
            logger.debug(f"[cache:hit] {key}")
            return json.loads(data)
        logger.debug(f"[cache:miss] {key}")
        return None

    @staticmethod
    async def set_detail(watchlist_id: UUID, watchlist: dict):
        key = WatchlistCache._detail_key(watchlist_id)
        await redis_client.set(key, json.dumps(watchlist, default=str), ex=WatchlistCache.DETAIL_TTL)

    @staticmethod
    async def invalidate_detail(watchlist_id: UUID):
        key = WatchlistCache._detail_key(watchlist_id)
        await redis_client.delete(key)
        logger.debug(f"[cache:invalidate] {key}")
