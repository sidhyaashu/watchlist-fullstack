from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.watchlist import Watchlist


class WatchlistRepository:

    @staticmethod
    async def create(db: AsyncSession, user_id: UUID, name: str) -> Watchlist:
        watchlist = Watchlist(user_id=user_id, name=name)
        db.add(watchlist)
        await db.commit()
        await db.refresh(watchlist)
        return watchlist

    @staticmethod
    async def get_by_user(
        db,
        user_id,
        skip: int = 0,
        limit: int = 20
    ):
        result = await db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, watchlist_id: UUID):
        result = await db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete(db: AsyncSession, watchlist_id: UUID):
        await db.execute(
            delete(Watchlist).where(Watchlist.id == watchlist_id)
        )
        await db.commit()