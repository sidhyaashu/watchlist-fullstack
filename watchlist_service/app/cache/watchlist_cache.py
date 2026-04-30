"""
WatchlistCache — thin domain key factory on top of CacheService.

Naming convention (WITHOUT the v1: prefix — CacheService adds it):
  List   → watchlists:{user_id}:{skip}:{limit}
  Detail → watchlist:{watchlist_id}
"""
from uuid import UUID
from typing import Optional

from app.core.cache_service import CacheService

# Separate TTLs per access pattern
_LIST_TTL = 300    # 5 min — changes on create/delete
_DETAIL_TTL = 600  # 10 min — changes rarely


def _list_key(user_id: UUID, skip: int, limit: int) -> str:
    return f"watchlists:{user_id}:{skip}:{limit}"


def _detail_key(watchlist_id: UUID) -> str:
    return f"watchlist:{watchlist_id}"


class WatchlistCache:

    # ─── List ──────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_list(user_id: UUID, skip: int, limit: int) -> Optional[list[dict]]:
        return await CacheService.get(_list_key(user_id, skip, limit))

    @staticmethod
    async def set_list(user_id: UUID, skip: int, limit: int, data: list[dict]):
        await CacheService.set(_list_key(user_id, skip, limit), data, _LIST_TTL)

    @staticmethod
    async def invalidate_list(user_id: UUID):
        # Nukes all paginated pages for this user atomically via SCAN
        await CacheService.delete_pattern(f"watchlists:{user_id}:*")

    # ─── Detail ────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_detail(watchlist_id: UUID) -> Optional[dict]:
        return await CacheService.get(_detail_key(watchlist_id))

    @staticmethod
    async def set_detail(watchlist_id: UUID, data: dict):
        await CacheService.set(_detail_key(watchlist_id), data, _DETAIL_TTL)

    @staticmethod
    async def invalidate_detail(watchlist_id: UUID):
        await CacheService.delete(_detail_key(watchlist_id))

    # ─── Stampede-Protected Read ────────────────────────────────────────────────

    @staticmethod
    async def get_or_set_list(user_id: UUID, skip: int, limit: int, fetcher) -> list[dict]:
        """
        Use this variant for the highest-traffic list endpoint.
        Stampede protection prevents DB overload when the page-0 cache expires.
        """
        return await CacheService.get_or_set(
            key=_list_key(user_id, skip, limit),
            ttl=_LIST_TTL,
            fetcher=fetcher,
        )
