from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

from app.market.repository import MarketRepository
from app.market.service import MarketService


def get_market_repository(db: AsyncSession = Depends(get_db)):
    return MarketRepository(db)


def get_market_service(
    repo: MarketRepository = Depends(get_market_repository),
):
    return MarketService(repo)