import json
from typing import Optional
from uuid import UUID

from app.cache.redis_client import redis_client
from app.utils.logger import logger


class WatchlistItemCache:
    ITEMS_TTL = 120  # 2 min — items change frequently (add/remove/reorder)

    @staticmethod
    def _items_key(watchlist_id: UUID, skip: int, limit: int) -> str:
        return f"watchlist_items:{watchlist_id}:{skip}:{limit}"

    @staticmethod
    async def get_items(watchlist_id: UUID, skip: int, limit: int) -> Optional[list[dict]]:
        key = WatchlistItemCache._items_key(watchlist_id, skip, limit)
        data = await redis_client.get(key)
        if data is not None:
            logger.debug(f"[cache:hit] {key}")
            return json.loads(data)
        logger.debug(f"[cache:miss] {key}")
        return None

    @staticmethod
    async def set_items(watchlist_id: UUID, skip: int, limit: int, items: list[dict]):
        key = WatchlistItemCache._items_key(watchlist_id, skip, limit)
        await redis_client.set(key, json.dumps(items, default=str), ex=WatchlistItemCache.ITEMS_TTL)

    @staticmethod
    async def invalidate_items(watchlist_id: UUID):
        """
        Scan and delete all paginated item-list keys for this watchlist.
        Called on add/remove/reorder — any write that changes the item set.
        """
        pattern = f"watchlist_items:{watchlist_id}:*"
        async for key in redis_client.scan_iter(match=pattern, count=100):
            await redis_client.delete(key)
        logger.debug(f"[cache:invalidate] pattern={pattern}")
