from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.market.models import CompanyMaster, NseMonthPrice


class MarketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_symbol(self, symbol: str):
        """
        Searches for instruments by symbol or name.
        Joins with the latest NseMonthPrice to provide current close price.
        """
        # 1. Subquery to identify the latest price record (Year/Month) per fincode
        latest_price_sub = (
            select(
                NseMonthPrice.fincode,
                func.max(NseMonthPrice.year * 100 + NseMonthPrice.month).label("latest_period")
            )
            .group_by(NseMonthPrice.fincode)
            .subquery()
        )

        query = (
            select(
                CompanyMaster.fincode.label("id"),
                CompanyMaster.symbol,
                CompanyMaster.compname.label("name"),
                NseMonthPrice.close.label("last_price")
            )
            .join(latest_price_sub, CompanyMaster.fincode == latest_price_sub.c.fincode)
            .join(
                NseMonthPrice,
                and_(
                    CompanyMaster.fincode == NseMonthPrice.fincode,
                    (NseMonthPrice.year * 100 + NseMonthPrice.month) == latest_price_sub.c.latest_period
                )
            )
            .where(
                (CompanyMaster.symbol.ilike(f"%{symbol}%")) | 
                (CompanyMaster.compname.ilike(f"%{symbol}%"))
            )
            .limit(20)
        )

        result = await self.db.execute(query)
        return result.all()
