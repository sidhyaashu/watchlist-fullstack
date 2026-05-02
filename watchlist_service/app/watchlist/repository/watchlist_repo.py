from sqlalchemy.future import select
from sqlalchemy import delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.watchlist.models.watchlist import Watchlist


class WatchlistRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def acquire_user_lock(self, user_id: int):
        query = text("SELECT pg_advisory_xact_lock(:user_id)")
        await self.db.execute(query, {"user_id": user_id})

    async def count_by_user(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(Watchlist.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_by_name(self, user_id: int, name: str) -> Watchlist | None:
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .where(func.lower(Watchlist.name) == name.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, name: str) -> Watchlist:
        watchlist = Watchlist(user_id=user_id, name=name)
        self.db.add(watchlist)
        await self.db.flush()
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
        await self.db.flush()