from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.watchlist.repository.watchlist_item_repo import WatchlistItemRepository
from app.market.service import MarketService
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException
from app.watchlist.schemas.watchlist_item import WatchlistItemResponse


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

    async def add_item(self, user_id: UUID, watchlist_id: UUID, data):
        # 🔹 Validate watchlist ownership
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Check item limit (Using COUNT query)
        count = await self.repo.count_items(watchlist_id)
        if count >= WatchlistItemService.MAX_ITEMS:
            raise BadRequestException("Watchlist item limit reached")

        # 🔹 Validate instrument exists (from DB)
        instrument = await self.market_service.get_instrument(int(data.instrument_id))
        if not instrument:
            raise BadRequestException("Invalid instrument")

        # 🔹 Add item with duplicate handling
        try:
            return await self.repo.add_item(watchlist_id, data)
        except IntegrityError:
            # Note: We expect the session rollback to be handled by the caller or a middleware
            # Alternatively, since we no longer pass db, we might need a way to rollback if needed, 
            # but usually FastAPI depends handle db commit/rollback on exception.
            raise BadRequestException("Item already exists in watchlist")

    async def remove_item(self, user_id: UUID, watchlist_id: UUID, instrument_id: str):
        # 🔹 Validate ownership
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        await self.repo.remove_item(watchlist_id, instrument_id)

    async def get_items(self, user_id: UUID, watchlist_id: UUID, skip=0, limit=50):
        limit = min(limit, 100)

        # 🔹 Validate ownership
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Get items (Repository now handles ORDER BY)
        items = await self.repo.get_items(watchlist_id, skip, limit)

        # 🔥 ENRICH WITH INSTRUMENT DATA
        instrument_ids = [int(item.instrument_id) for item in items]
        instruments = await self.market_service.get_bulk_instruments(instrument_ids)
        instrument_map = {str(inst.id): inst for inst in instruments}

        enriched = []
        for item in items:
            inst = instrument_map.get(str(item.instrument_id))
            
            # Use model_validate for safe conversion, then add enrichment fields
            resp_data = WatchlistItemResponse.model_validate(item)
            if inst:
                resp_data.name = getattr(inst, "name", None)
                resp_data.last_price = getattr(inst, "last_price", None)
                resp_data.change_percent = getattr(inst, "change_percent", None)
            
            enriched.append(resp_data)

        return enriched

    async def reorder_items(self, user_id: UUID, watchlist_id: UUID, updates):
        # 🔹 Validate ownership
        watchlist = await self.watchlist_repo.get_by_id(watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Update positions using batch operation
        await self.repo.batch_update_positions(watchlist_id, updates)