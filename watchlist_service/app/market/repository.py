from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.market.models import Instrument


class MarketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_instrument_by_id(self, instrument_id: int):
        result = await self.db.execute(
            select(Instrument).where(Instrument.id == instrument_id)
        )
        return result.scalar_one_or_none()

    async def get_instruments_by_ids(self, ids: list[int]):
        result = await self.db.execute(
            select(Instrument).where(Instrument.id.in_(ids))
        )
        return result.scalars().all()

    async def search_by_symbol(self, symbol: str):
        result = await self.db.execute(
            select(Instrument).where(Instrument.symbol.ilike(f"%{symbol}%"))
        )
        return result.scalars().all()