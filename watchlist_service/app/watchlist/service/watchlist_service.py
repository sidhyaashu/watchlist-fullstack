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
        name = name.strip()
        if not name:
            raise BadRequestException("Watchlist name cannot be empty")

        # 🔹 Wrap entire critical section in a single explicit transaction
        # pg_advisory_xact_lock serializes concurrent creates for the same user.
        # All DB ops are inside the transaction — lock is held until commit.
        # Cache invalidation happens AFTER commit so we never serve stale data.
        async with self.repo.db.begin():
            await self.repo.acquire_user_lock(user_id)

            existing_name = await self.repo.get_by_name(user_id, name)
            if existing_name:
                raise BadRequestException(f"Watchlist '{name}' already exists")

            count = await self.repo.count_by_user(user_id)
            if count >= WatchlistService.MAX_WATCHLISTS:
                logger.warning(f"[watchlist] limit reached user={user_id} count={count}")
                raise BadRequestException("Watchlist limit reached")

            watchlist = await self.repo.create(user_id, name)
            # Serialize while session still alive (attributes loaded)
            response = WatchlistResponse.model_validate(watchlist)

        # ✅ Outside transaction — invalidate ALL paginated list pages for this user
        await WatchlistCache.invalidate_list(user_id)
        logger.info(f"[watchlist] created name={name} user={user_id} id={response.id}")

        return response

    async def get_user_watchlists(self, user_id: UUID, skip: int = 0, limit: int = 20) -> list[WatchlistResponse]:
        limit = min(limit, 100)

        # 🔹 Stampede-protected cache-aside for the hottest endpoint.
        # On expiry, only ONE request fetches from DB; others wait then read from cache.
        async def _fetch() -> list[dict]:
            async with self.repo.db.begin():
                watchlists = await self.repo.get_by_user(user_id, skip, limit)
                return [WatchlistResponse.model_validate(w).model_dump() for w in watchlists]

        raw = await WatchlistCache.get_or_set_list(user_id, skip, limit, _fetch)
        return [WatchlistResponse.model_validate(w) for w in raw]

    async def get_watchlist(self, user_id: UUID, watchlist_id: UUID) -> WatchlistResponse:
        # 🔹 Cache-aside: single watchlist detail
        cached = await WatchlistCache.get_detail(watchlist_id)
        if cached is not None:
            detail = WatchlistResponse.model_validate(cached)
            # Ownership check still enforced even on cache hit
            if str(cached.get("user_id")) != str(user_id):
                raise UnauthorizedException()
            return detail

        async with self.repo.db.begin():
            watchlist = await self.repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        response = WatchlistResponse.model_validate(watchlist)

        # Cache includes user_id for ownership validation on cache hits
        data = response.model_dump()
        data["user_id"] = str(user_id)
        await WatchlistCache.set_detail(watchlist_id, data)

        return response

    async def delete_watchlist(self, user_id: UUID, watchlist_id: UUID) -> None:
        async with self.repo.db.begin():
            watchlist = await self.repo.get_by_id(watchlist_id)

            if not watchlist:
                raise NotFoundException("Watchlist not found")

            if watchlist.user_id != user_id:
                logger.warning(f"[watchlist] unauthorized delete attempt user={user_id} id={watchlist_id}")
                raise UnauthorizedException()

            await self.repo.delete(watchlist_id)

        # Invalidate both the list pages and the single detail key
        await WatchlistCache.invalidate_list(user_id)
        await WatchlistCache.invalidate_detail(watchlist_id)
        logger.info(f"[watchlist] deleted id={watchlist_id} user={user_id}")