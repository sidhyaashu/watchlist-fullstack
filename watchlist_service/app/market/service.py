from app.market.repository import MarketRepository


class MarketService:
    def __init__(self, repo: MarketRepository):
        self.repo = repo

    async def search_instruments(self, symbol: str):
        return await self.repo.search_by_symbol(symbol)

    async def get_popular_instruments(self, limit: int = 8):
        return await self.repo.get_popular(limit)
