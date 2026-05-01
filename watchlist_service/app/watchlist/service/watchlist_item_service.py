from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.watchlist.repository.watchlist_item_repo import WatchlistItemRepository
from app.market.service import MarketService
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException
from app.cache.watchlist_item_cache import WatchlistItemCache
from app.watchlist.schemas.watchlist_item import WatchlistItemResponse
from app.utils.logger import logger


class WatchlistItemService:

    MAX_ITEMS = 100  # business rule

    def __init__(
        self,
        repo: WatchlistItemRepository,
        watchlist_repo: WatchlistRepository,
        market_service: MarketService
    ):
        self.repo = repo
        self.watchlist_repo = watchlist_repo
        self.market_service = market_service

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

            instrument = await self.market_service.get_instrument(int(data.instrument_id))
            if not instrument:
                raise BadRequestException("Invalid instrument")

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

        items = await self.repo.get_items(watchlist_id, skip, limit)

        # 🔥 Bulk enrich with Azure market data
        fincodes = [int(item.instrument_id) for item in items]
        basic_infos, prices = await self.market_service.get_bulk_instruments(fincodes)
        
        # Build maps for efficient merging
        info_map = {str(inst.FINCODE): inst for inst in basic_infos}
        price_map = {str(p.Fincode): p for p in prices}

        enriched: list[WatchlistItemResponse] = []
        for item in items:
            resp = WatchlistItemResponse.model_validate(item)
            info = info_map.get(str(item.instrument_id))
            price_data = price_map.get(str(item.instrument_id))
            
            if info:
                resp.name = getattr(info, "COMPNAME", None)
                resp.symbol = getattr(info, "SYMBOL", resp.symbol)
            
            if price_data:
                resp.last_price = getattr(price_data, "Close", None)
                # Note: change_percent logic could be added here if you have 
                # comparison with previous close
            
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