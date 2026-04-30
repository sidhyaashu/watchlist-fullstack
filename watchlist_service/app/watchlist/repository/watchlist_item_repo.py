from sqlalchemy import delete, update, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.watchlist.models.watchlist_item import WatchlistItem


class WatchlistItemRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_item(self, watchlist_id: UUID, data) -> WatchlistItem:
        item = WatchlistItem(
            watchlist_id=watchlist_id,
            instrument_id=data.instrument_id,
            symbol=data.symbol,
            exchange=data.exchange,
        )
        self.db.add(item)
        await self.db.flush()  # push to DB within open transaction; no commit here
        return item

    async def count_items(self, watchlist_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(WatchlistItem.watchlist_id == watchlist_id)
        )
        return result.scalar() or 0

    async def get_items(
        self,
        watchlist_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> list[WatchlistItem]:
        result = await self.db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .order_by(WatchlistItem.position.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def remove_item(self, watchlist_id: UUID, instrument_id: str):
        await self.db.execute(
            delete(WatchlistItem).where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.instrument_id == instrument_id
            )
        )
        await self.db.flush()

    async def update_position(
        self,
        watchlist_id: UUID,
        instrument_id: str,
        position: int
    ):
        await self.db.execute(
            update(WatchlistItem)
            .where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.instrument_id == instrument_id
            )
            .values(position=position)
        )
        await self.db.flush()

    async def batch_update_positions(self, watchlist_id: UUID, updates: list):
        """Efficiently update multiple positions within the caller's transaction."""
        for item in updates:
            await self.db.execute(
                update(WatchlistItem)
                .where(
                    WatchlistItem.watchlist_id == watchlist_id,
                    WatchlistItem.instrument_id == item.instrument_id
                )
                .values(position=item.position)
            )
        await self.db.flush()