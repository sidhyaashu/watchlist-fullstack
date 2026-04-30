from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repository.watchlist_repo import WatchlistRepository
from app.repository.watchlist_item_repo import WatchlistItemRepository
from app.integrations.instrument_query import InstrumentQuery
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException
from app.schemas.watchlist_item import WatchlistItemResponse


class WatchlistItemService:

    MAX_ITEMS = 100  # business rule

    @staticmethod
    async def add_item(db: AsyncSession, user_id: UUID, watchlist_id: UUID, data):
        # 🔹 Validate watchlist ownership
        watchlist = await WatchlistRepository.get_by_id(db, watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Check item limit (Using COUNT query)
        count = await WatchlistItemRepository.count_items(db, watchlist_id)
        if count >= WatchlistItemService.MAX_ITEMS:
            raise BadRequestException("Watchlist item limit reached")

        # 🔹 Validate instrument exists (from DB)
        instrument = await InstrumentQuery.get_by_id(db, data.instrument_id)
        if not instrument:
            raise BadRequestException("Invalid instrument")

        # 🔹 Add item with duplicate handling
        try:
            return await WatchlistItemRepository.add_item(db, watchlist_id, data)
        except IntegrityError:
            await db.rollback()
            raise BadRequestException("Item already exists in watchlist")

    @staticmethod
    async def remove_item(db: AsyncSession, user_id: UUID, watchlist_id: UUID, instrument_id: str):
        # 🔹 Validate ownership
        watchlist = await WatchlistRepository.get_by_id(db, watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        await WatchlistItemRepository.remove_item(db, watchlist_id, instrument_id)

    @staticmethod
    async def get_items(db: AsyncSession, user_id: UUID, watchlist_id: UUID, skip=0, limit=50):
        limit = min(limit, 100)

        # 🔹 Validate ownership
        watchlist = await WatchlistRepository.get_by_id(db, watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Get items (Repository now handles ORDER BY)
        items = await WatchlistItemRepository.get_items(db, watchlist_id, skip, limit)

        # 🔥 ENRICH WITH INSTRUMENT DATA
        instrument_ids = [item.instrument_id for item in items]
        instruments = await InstrumentQuery.bulk_get(db, instrument_ids)
        instrument_map = {inst.id: inst for inst in instruments}

        enriched = []
        for item in items:
            inst = instrument_map.get(item.instrument_id)
            
            # Use model_validate for safe conversion, then add enrichment fields
            resp_data = WatchlistItemResponse.model_validate(item)
            resp_data.name = getattr(inst, "name", None)
            resp_data.last_price = getattr(inst, "last_price", None)
            resp_data.change_percent = getattr(inst, "change_percent", None)
            
            enriched.append(resp_data)

        return enriched

    @staticmethod
    async def reorder_items(db: AsyncSession, user_id: UUID, watchlist_id: UUID, updates):
        # 🔹 Validate ownership
        watchlist = await WatchlistRepository.get_by_id(db, watchlist_id)

        if not watchlist:
            raise NotFoundException("Watchlist not found")

        if watchlist.user_id != user_id:
            raise UnauthorizedException()

        # 🔹 Update positions using batch operation
        await WatchlistItemRepository.batch_update_positions(db, watchlist_id, updates)