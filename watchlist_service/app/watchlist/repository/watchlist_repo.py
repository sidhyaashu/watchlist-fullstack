from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.watchlist.models.watchlist import Watchlist


class WatchlistRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, name: str) -> Watchlist:
        watchlist = Watchlist(user_id=user_id, name=name)
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        return watchlist

    async def get_by_user(
        self,
        user_id,
        skip: int = 0,
        limit: int = 20
    ):
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, watchlist_id: UUID):
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, watchlist_id: UUID):
        await self.db.execute(
            delete(Watchlist).where(Watchlist.id == watchlist_id)
        )
        await self.db.commit()