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
        from app.market.models import Instrument
        from datetime import datetime, timezone
        
        results = await self.repo.search_by_symbol(symbol)
        if results:
            return results
            
        mock_instruments = [
            {"id": 1, "symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "last_price": 175.50, "updated_at": datetime.now(timezone.utc)},
            {"id": 2, "symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "last_price": 405.10, "updated_at": datetime.now(timezone.utc)},
            {"id": 3, "symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "last_price": 190.20, "updated_at": datetime.now(timezone.utc)},
            {"id": 4, "symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "last_price": 850.30, "updated_at": datetime.now(timezone.utc)},
            {"id": 5, "symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ", "last_price": 180.40, "updated_at": datetime.now(timezone.utc)},
            {"id": 6, "symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "last_price": 165.70, "updated_at": datetime.now(timezone.utc)},
        ]
        
        symbol_lower = symbol.lower()
        filtered = [
            Instrument(**item) 
            for item in mock_instruments 
            if symbol_lower in item["symbol"].lower() or symbol_lower in item["name"].lower()
        ]
        return filtered