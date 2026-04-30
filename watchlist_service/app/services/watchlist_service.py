from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.watchlist_repo import WatchlistRepository
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.cache.watchlist_cache import WatchlistCache
from app.schemas.watchlist import WatchlistResponse


class WatchlistService:

    MAX_WATCHLISTS = 10  # business rule

    @staticmethod
    async def create_watchlist(db: AsyncSession, user_id: UUID, name: str):
        # 🔹 Check limit
        existing = await WatchlistRepository.get_by_user(db, user_id)
        if len(existing) >= WatchlistService.MAX_WATCHLISTS:
            raise BadRequestException("Watchlist limit reached")

        # 🔹 Create
        watchlist = await WatchlistRepository.create(db, user_id, name)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)
        
        return watchlist

    @staticmethod
    async def get_user_watchlists(db: AsyncSession, user_id: UUID, skip=0, limit=20):
        limit = min(limit, 100)
        
        # 🔹 Try Cache (only for first page default query)
        if skip == 0 and limit == 20:
            cached = await WatchlistCache.get_watchlists(user_id)
            if cached:
                return cached

        watchlists = await WatchlistRepository.get_by_user(db, user_id, skip, limit)
        
        # 🔹 Convert to serializable format for cache
        serializable = [WatchlistResponse.model_validate(w).model_dump() for w in watchlists]
        
        if skip == 0 and limit == 20:
            await WatchlistCache.set_watchlists(user_id, serializable)
            
        return watchlists

    @staticmethod
    async def delete_watchlist(db: AsyncSession, user_id: UUID, watchlist_id: UUID):
        watchlist = await WatchlistRepository.get_by_id(db, watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        await WatchlistRepository.delete(db, watchlist_id)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)