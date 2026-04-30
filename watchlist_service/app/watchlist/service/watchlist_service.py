from uuid import UUID

from app.utils.logger import logger
from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.cache.watchlist_cache import WatchlistCache
from app.watchlist.schemas.watchlist import WatchlistResponse


class WatchlistService:

    MAX_WATCHLISTS = 10  # business rule

    def __init__(self, repo: WatchlistRepository):
        self.repo = repo

    async def create_watchlist(self, user_id: UUID, name: str) -> WatchlistResponse:
        # 🔹 Input Validation
        if not name or not name.strip():
            logger.warning(f"User {user_id} attempted to create watchlist with empty name")
            raise BadRequestException("Watchlist name cannot be empty")
        
        name = name.strip()

        # 🔹 Race Condition Prevention & DB count check
        # Acquire advisory lock to serialize requests for this user
        await self.repo.acquire_user_lock(user_id)

        # 🔹 Check duplicate name
        existing_name = await self.repo.get_by_name(user_id, name)
        if existing_name:
            logger.warning(f"User {user_id} attempted to create duplicate watchlist '{name}'")
            raise BadRequestException(f"Watchlist with name '{name}' already exists")

        # 🔹 Check limit efficiently
        count = await self.repo.count_by_user(user_id)
        if count >= WatchlistService.MAX_WATCHLISTS:
            logger.warning(f"User {user_id} reached watchlist limit ({count})")
            raise BadRequestException("Watchlist limit reached")

        # 🔹 Create
        watchlist = await self.repo.create(user_id, name)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)
        logger.info(f"Created watchlist '{name}' for user {user_id}")
        
        return WatchlistResponse.model_validate(watchlist)

    async def get_user_watchlists(self, user_id: UUID, skip=0, limit=20) -> list[WatchlistResponse]:
        limit = min(limit, 100)
        
        # 🔹 Try Cache (only for first page default query)
        if skip == 0 and limit == 20:
            cached = await WatchlistCache.get_watchlists(user_id)
            if cached is not None:
                logger.debug(f"Cache hit for user {user_id} watchlists")
                return [WatchlistResponse.model_validate(w) for w in cached]

        logger.debug(f"Cache miss or paginated request for user {user_id} watchlists")
        watchlists = await self.repo.get_by_user(user_id, skip, limit)
        response_models = [WatchlistResponse.model_validate(w) for w in watchlists]
        
        # 🔹 Convert to serializable format for cache
        if skip == 0 and limit == 20:
            serializable = [w.model_dump() for w in response_models]
            await WatchlistCache.set_watchlists(user_id, serializable)
            
        return response_models

    async def delete_watchlist(self, user_id: UUID, watchlist_id: UUID) -> None:
        watchlist = await self.repo.get_by_id(watchlist_id)

        if not watchlist:
            logger.warning(f"User {user_id} attempted to delete non-existent watchlist {watchlist_id}")
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            logger.error(f"Unauthorized deletion attempt by user {user_id} on watchlist {watchlist_id}")
            raise UnauthorizedException()

        await self.repo.delete(watchlist_id)
        
        # 🔹 Invalidate cache
        await WatchlistCache.invalidate(user_id)
        logger.info(f"Deleted watchlist {watchlist_id} for user {user_id}")