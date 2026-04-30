"""
WatchlistItemCache — thin domain key factory on top of CacheService.

Naming convention (WITHOUT the v1: prefix — CacheService adds it):
  Items → watchlist_items:{watchlist_id}:{skip}:{limit}
"""
from uuid import UUID
from typing import Optional

from app.core.cache_service import CacheService

_ITEMS_TTL = 120  # 2 min — items change frequently


def _items_key(watchlist_id: UUID, skip: int, limit: int) -> str:
    return f"watchlist_items:{watchlist_id}:{skip}:{limit}"


class WatchlistItemCache:

    @staticmethod
    async def get_items(watchlist_id: UUID, skip: int, limit: int) -> Optional[list[dict]]:
        return await CacheService.get(_items_key(watchlist_id, skip, limit))

    @staticmethod
    async def set_items(watchlist_id: UUID, skip: int, limit: int, data: list[dict]):
        await CacheService.set(_items_key(watchlist_id, skip, limit), data, _ITEMS_TTL)

    @staticmethod
    async def invalidate_items(watchlist_id: UUID):
        # Nukes ALL paginated pages for this watchlist via SCAN
        await CacheService.delete_pattern(f"watchlist_items:{watchlist_id}:*")

    @staticmethod
    async def get_or_set_items(watchlist_id: UUID, skip: int, limit: int, fetcher) -> list[dict]:
        """Stampede-protected variant for high-traffic item reads."""
        return await CacheService.get_or_set(
            key=_items_key(watchlist_id, skip, limit),
            ttl=_ITEMS_TTL,
            fetcher=fetcher,
        )
