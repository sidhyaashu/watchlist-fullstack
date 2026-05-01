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
    user_id: UUID = Depends(get_current_user),
    market_service: MarketService = Depends(get_market_service),
):
    """Search for instruments by symbol or name."""
    return await market_service.search_instruments(q)
