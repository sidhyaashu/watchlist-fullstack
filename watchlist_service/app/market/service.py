from app.market.repository import MarketRepository


class MarketService:
    def __init__(self, repo: MarketRepository):
        self.repo = repo

    async def get_instrument(self, fincode: int):
        return await self.repo.get_instrument_by_id(fincode)

    async def get_bulk_instruments(self, fincodes: list[int]):
        # First get basic info from CompanyMaster
        from sqlalchemy import select
        from app.market.models import CompanyMaster
        
        result = await self.repo.db.execute(
            select(CompanyMaster).where(CompanyMaster.FINCODE.in_(fincodes))
        )
        basic_infos = result.scalars().all()
        
        # Then get prices
        prices = await self.repo.get_prices_for_fincodes(fincodes)
        
        return basic_infos, prices

    async def search_instruments(self, symbol: str):
        return await self.repo.search_by_symbol(symbol)