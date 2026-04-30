from sqlalchemy import delete, update, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.watchlist_item import WatchlistItem


class WatchlistItemRepository:

    @staticmethod
    async def add_item(db: AsyncSession, watchlist_id: UUID, data):
        item = WatchlistItem(
            watchlist_id=watchlist_id,
            instrument_id=data.instrument_id,
            symbol=data.symbol,
            exchange=data.exchange,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def count_items(db: AsyncSession, watchlist_id: UUID) -> int:
        result = await db.execute(
            select(func.count()).where(WatchlistItem.watchlist_id == watchlist_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def get_items(
        db: AsyncSession,
        watchlist_id: UUID,
        skip: int = 0,
        limit: int = 50
    ):
        result = await db.execute(
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .order_by(WatchlistItem.position.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def remove_item(db: AsyncSession, watchlist_id: UUID, instrument_id: str):
        await db.execute(
            delete(WatchlistItem).where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.instrument_id == instrument_id
            )
        )
        await db.commit()

    @staticmethod
    async def update_position(
        db: AsyncSession,
        watchlist_id: UUID,
        instrument_id: str,
        position: int
    ):
        await db.execute(
            update(WatchlistItem)
            .where(
                WatchlistItem.watchlist_id == watchlist_id,
                WatchlistItem.instrument_id == instrument_id
            )
            .values(position=position)
        )
        await db.commit()

    @staticmethod
    async def batch_update_positions(
        db: AsyncSession,
        watchlist_id: UUID,
        updates: list
    ):
        """Efficiently update multiple positions in a single transaction."""
        for item in updates:
            await db.execute(
                update(WatchlistItem)
                .where(
                    WatchlistItem.watchlist_id == watchlist_id,
                    WatchlistItem.instrument_id == item.instrument_id
                )
                .values(position=item.position)
            )
        await db.commit()