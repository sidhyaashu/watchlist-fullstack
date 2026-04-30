from app.market.repository import MarketRepository


class MarketService:
    def __init__(self, repo: MarketRepository):
        self.repo = repo

    async def get_instrument(self, instrument_id: int):
        instrument = await self.repo.get_instrument_by_id(instrument_id)

        if not instrument:
            return None

        return instrument

    async def get_bulk_instruments(self, ids: list[int]):
        return await self.repo.get_instruments_by_ids(ids)

    async def search_instruments(self, symbol: str):
        return await self.repo.search_by_symbol(symbol)