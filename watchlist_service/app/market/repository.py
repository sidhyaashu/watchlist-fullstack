from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.market.models import CompanyMaster, NseMonthPrice, Instrument


class MarketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_instrument_by_id(self, fincode: int):
        result = await self.db.execute(
            select(CompanyMaster).where(CompanyMaster.FINCODE == fincode)
        )
        return result.scalar_one_or_none()

    async def get_prices_for_fincodes(self, fincodes: list[int]):
        """
        Fetches the latest prices for a list of FINCODEs.
        Uses a subquery to find the latest (max Year/Month) for each Fincode.
        """
        if not fincodes:
            return []

        # Subquery to find the latest Month/Year per Fincode
        latest_sub = (
            select(
                NseMonthPrice.Fincode,
                func.max(NseMonthPrice.Year * 100 + NseMonthPrice.Month).label("latest_period")
            )
            .where(NseMonthPrice.Fincode.in_(fincodes))
            .group_by(NseMonthPrice.Fincode)
            .subquery()
        )

        query = (
            select(NseMonthPrice)
            .join(
                latest_sub,
                and_(
                    NseMonthPrice.Fincode == latest_sub.c.Fincode,
                    (NseMonthPrice.Year * 100 + NseMonthPrice.Month) == latest_sub.c.latest_period
                )
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def search_by_symbol(self, symbol: str):
        result = await self.db.execute(
            select(CompanyMaster)
            .where(
                (CompanyMaster.SYMBOL.ilike(f"%{symbol}%")) | 
                (CompanyMaster.COMPNAME.ilike(f"%{symbol}%"))
            )
            .limit(20)
        )
        return result.scalars().all()