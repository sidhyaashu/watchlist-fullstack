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

    async def get_items(self, watchlist_id: UUID, skip: int = 0, limit: int = 50):
        """
        Fetches watchlist items enriched with market data in a single SQL query.
        Calculates 52W range by aggregating historical NseMonthPrice data.
        """
        from app.market.models import CompanyMaster, NseMonthPrice, CompanyEquity
        from sqlalchemy import and_

        # 1. Subquery to identify the latest price record (Year/Month) per fincode
        latest_price_sub = (
            select(
                NseMonthPrice.fincode,
                func.max(NseMonthPrice.year * 100 + NseMonthPrice.month).label("latest_period")
            )
            .group_by(NseMonthPrice.fincode)
            .subquery()
        )



        # 2. Subquery to calculate the historical High and Low (52W Range)
        range_sub = (
            select(
                NseMonthPrice.fincode,
                func.max(NseMonthPrice.high).label("year_high"),
                func.min(NseMonthPrice.low).label("year_low")
            )
            .group_by(NseMonthPrice.fincode)
            .subquery()
        )



        # 3. Main query joining items -> company info -> latest price -> high/low range -> equity data
        query = (
            select(
                WatchlistItem,
                CompanyMaster.compname.label("compname"),
                CompanyMaster.symbol.label("symbol"),
                CompanyMaster.industry,
                NseMonthPrice.close.label("last_price"),
                NseMonthPrice.open.label("open_price"),
                range_sub.c.year_high,
                range_sub.c.year_low,
                CompanyEquity.mcap.label("mcap"),
                CompanyEquity.ttmpe.label("pe")
            )
            .outerjoin(CompanyMaster, WatchlistItem.instrument_id == CompanyMaster.fincode)
            .outerjoin(latest_price_sub, WatchlistItem.instrument_id == latest_price_sub.c.fincode)
            .outerjoin(
                NseMonthPrice,
                and_(
                    WatchlistItem.instrument_id == NseMonthPrice.fincode,
                    (NseMonthPrice.year * 100 + NseMonthPrice.month) == latest_price_sub.c.latest_period
                )
            )
            .outerjoin(range_sub, WatchlistItem.instrument_id == range_sub.c.fincode)
            .outerjoin(CompanyEquity, WatchlistItem.instrument_id == CompanyEquity.fincode)
            .where(WatchlistItem.watchlist_id == watchlist_id)


            .order_by(WatchlistItem.position.asc())
            .offset(skip)
            .limit(limit)
        )


        result = await self.db.execute(query)
        return result.all()



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