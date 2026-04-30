from uuid import UUID

from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.cache.watchlist_cache import WatchlistCache
from app.watchlist.schemas.watchlist import WatchlistResponse


class WatchlistService:

    MAX_WATCHLISTS = 10  # business rule

    def __init__(self, repo: WatchlistRepository):
        self.repo = repo

    async def create_watchlist(self, user_id: UUID, name: str):
        # 🔹 Check limit
        existing = await self.repo.get_by_user(user_id)
        if len(existing) >= WatchlistService.MAX_WATCHLISTS:
            raise BadRequestException("Watchlist limit reached")

        # 🔹 Create
        watchlist = await self.repo.create(user_id, name)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)
        
        return watchlist

    async def get_user_watchlists(self, user_id: UUID, skip=0, limit=20):
        limit = min(limit, 100)
        
        # 🔹 Try Cache (only for first page default query)
        if skip == 0 and limit == 20:
            cached = await WatchlistCache.get_watchlists(user_id)
            if cached:
                return cached

        watchlists = await self.repo.get_by_user(user_id, skip, limit)
        
        # 🔹 Convert to serializable format for cache
        serializable = [WatchlistResponse.model_validate(w).model_dump() for w in watchlists]
        
        if skip == 0 and limit == 20:
            await WatchlistCache.set_watchlists(user_id, serializable)
            
        return watchlists

    async def delete_watchlist(self, user_id: UUID, watchlist_id: UUID):
        watchlist = await self.repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        await self.repo.delete(watchlist_id)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)