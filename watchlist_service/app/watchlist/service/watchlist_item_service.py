from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.watchlist.repository.watchlist_item_repo import WatchlistItemRepository
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException
from app.cache.watchlist_item_cache import WatchlistItemCache
from app.watchlist.schemas.watchlist_item import WatchlistItemResponse
from app.utils.logger import logger


class WatchlistItemService:

    MAX_ITEMS = 100  # business rule

    def __init__(
        self,
        repo: WatchlistItemRepository,
        watchlist_repo: WatchlistRepository
    ):
        self.repo = repo
        self.watchlist_repo = watchlist_repo

    async def _get_owned_watchlist(self, user_id: int, watchlist_id: UUID):
        """Reusable ownership guard — raises if missing or unauthorized."""
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)
        if not watchlist:
            raise NotFoundException("Watchlist not found")
        if watchlist.user_id != user_id:
            raise UnauthorizedException()
        return watchlist

    async def add_item(self, user_id: int, watchlist_id: UUID, data):
        async with self.repo.db.begin():
            await self._get_owned_watchlist(user_id, watchlist_id)

            count = await self.repo.count_items(watchlist_id)
            if count >= WatchlistItemService.MAX_ITEMS:
                raise BadRequestException("Watchlist item limit reached")

            try:
                item = await self.repo.add_item(watchlist_id, data)
                response = WatchlistItemResponse.model_validate(item)
            except IntegrityError:
                raise BadRequestException("Item already exists in watchlist")

        # Invalidate all item pages for this watchlist
        await WatchlistItemCache.invalidate_items(watchlist_id)
        logger.info(f"[item] added instrument={data.instrument_id} watchlist={watchlist_id}")

        return response

    async def remove_item(self, user_id: int, watchlist_id: UUID, instrument_id: str):
        async with self.repo.db.begin():
            await self._get_owned_watchlist(user_id, watchlist_id)
            await self.repo.remove_item(watchlist_id, instrument_id)

        await WatchlistItemCache.invalidate_items(watchlist_id)
        logger.info(f"[item] removed instrument={instrument_id} watchlist={watchlist_id}")

    async def get_items(self, user_id: int, watchlist_id: UUID, skip: int = 0, limit: int = 50) -> list[WatchlistItemResponse]:
        limit = min(limit, 100)

        # 🔹 Ownership check
        await self._get_owned_watchlist(user_id, watchlist_id)

        # 🔹 Cache-aside
        cached = await WatchlistItemCache.get_items(watchlist_id, skip, limit)
        if cached is not None:
            return [WatchlistItemResponse.model_validate(i) for i in cached]

        # 🔥 Single high-performance SQL query joining items + market data
        rows = await self.repo.get_items(watchlist_id, skip, limit)

        enriched: list[WatchlistItemResponse] = []
        for row in rows:
            item, comp_name, symbol, industry, last_price, open_price, year_high, year_low = row
            
            resp = WatchlistItemResponse.model_validate(item)
            # Override with fresh market data from JOIN
            if comp_name:
                resp.name = comp_name
            if symbol:
                resp.symbol = symbol
            if industry:
                resp.sector = industry
            if last_price:
                resp.last_price = last_price
            
            # Calculate change % if both prices available
            if last_price and open_price and open_price != 0:
                resp.change_percent = ((last_price - open_price) / open_price) * 100

            if year_high:
                resp.year_high = year_high
            if year_low:
                resp.year_low = year_low
            
            enriched.append(resp)



        # Cache the fully-enriched list
        await WatchlistItemCache.set_items(
            watchlist_id, skip, limit,
            [r.model_dump() for r in enriched]
        )

        return enriched



    async def reorder_items(self, user_id: UUID, watchlist_id: UUID, updates):
        async with self.repo.db.begin():
            await self._get_owned_watchlist(user_id, watchlist_id)
            await self.repo.batch_update_positions(watchlist_id, updates)

        await WatchlistItemCache.invalidate_items(watchlist_id)
        logger.info(f"[item] reordered watchlist={watchlist_id}")