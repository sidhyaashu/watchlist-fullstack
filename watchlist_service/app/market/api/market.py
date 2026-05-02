from fastapi import APIRouter, Depends, Query
from typing import List
from uuid import UUID

from app.api.deps import get_current_user
from app.market.dependencies import get_market_service
from app.market.service import MarketService
from app.market.schemas import InstrumentResponse

router = APIRouter()

@router.get("/search", response_model=List[InstrumentResponse])
async def search_instruments(
    q: str = Query(..., min_length=1, description="Symbol to search for"),
    user_id: int = Depends(get_current_user),
    market_service: MarketService = Depends(get_market_service),
):
    """Search for instruments by symbol or name."""
    return await market_service.search_instruments(q)


@router.get("/popular", response_model=List[InstrumentResponse])
async def get_popular_instruments(
    limit: int = Query(8, ge=1, le=20, description="Number of popular instruments to return"),
    user_id: int = Depends(get_current_user),
    market_service: MarketService = Depends(get_market_service),
):
    """Return top instruments by market cap — shown in the modal before user types."""
    return await market_service.get_popular_instruments(limit)
