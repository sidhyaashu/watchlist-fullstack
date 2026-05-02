from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, literal_column, case

from app.market.models import CompanyMaster, NseMonthPrice


class MarketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_by_symbol(self, symbol: str):
        """
        Searches for instruments by symbol or name.
        Uses OUTER JOINs to ensure companies appear even if price or equity data is missing.
        """
        from app.market.models import CompanyEquity

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
                CompanyMaster.symbol.label("symbol"),
                CompanyMaster.compname.label("name"),
                literal_column("'NSE'").label("exchange"),
                NseMonthPrice.close.label("last_price"),
                CompanyEquity.mcap,
                CompanyEquity.ttmpe.label("pe")
            )
            .outerjoin(latest_price_sub, CompanyMaster.fincode == latest_price_sub.c.fincode)
            .outerjoin(
                NseMonthPrice,
                and_(
                    CompanyMaster.fincode == NseMonthPrice.fincode,
                    (NseMonthPrice.year * 100 + NseMonthPrice.month) == latest_price_sub.c.latest_period
                )
            )
            .outerjoin(CompanyEquity, CompanyMaster.fincode == CompanyEquity.fincode)
            .where(
                (CompanyMaster.symbol.ilike(f"{symbol}%")) | 
                (CompanyMaster.compname.ilike(f"%{symbol}%"))
            )
            .order_by(
                case(
                    (CompanyMaster.symbol.ilike(f"{symbol}%"), 0),
                    else_=1
                ),
                CompanyMaster.symbol.asc()
            )
            .limit(20)
        )

        result = await self.db.execute(query)
        return result.all()

    async def get_popular(self, limit: int = 8):
        """
        Returns top instruments by market cap — used for the 'Popular on InvestKaro'
        default list shown in the Add Stock modal before the user starts typing.
        """
        from app.market.models import CompanyEquity

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
                CompanyMaster.symbol.label("symbol"),
                CompanyMaster.compname.label("name"),
                literal_column("'NSE'").label("exchange"),
                NseMonthPrice.close.label("last_price"),
                CompanyEquity.mcap,
                CompanyEquity.ttmpe.label("pe"),
            )
            .outerjoin(latest_price_sub, CompanyMaster.fincode == latest_price_sub.c.fincode)
            .outerjoin(
                NseMonthPrice,
                and_(
                    CompanyMaster.fincode == NseMonthPrice.fincode,
                    (NseMonthPrice.year * 100 + NseMonthPrice.month) == latest_price_sub.c.latest_period
                )
            )
            .outerjoin(CompanyEquity, CompanyMaster.fincode == CompanyEquity.fincode)
            .where(
                CompanyEquity.mcap.isnot(None),
                NseMonthPrice.close.isnot(None),
            )
            .order_by(CompanyEquity.mcap.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.all()
