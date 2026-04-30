from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime



# 🔹 Add Instrument to Watchlist
class WatchlistItemCreate(BaseModel):
    instrument_id: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: str = Field(..., min_length=1, max_length=10)


# 🔹 Update Position (ordering)
class WatchlistItemReorder(BaseModel):
    instrument_id: str
    position: int


# 🔹 Response Model
class WatchlistItemResponse(BaseModel):
    id: UUID
    instrument_id: str
    symbol: str
    exchange: str
    position: Optional[int]
    added_at: Optional[datetime]

    # future enrichment fields (from instrument table)
    name: Optional[str] = None
    last_price: Optional[float] = None
    change_percent: Optional[float] = None

    class Config:
        from_attributes = True

class BulkAddItems(BaseModel):
    items: list[WatchlistItemCreate]


class WatchlistDetailResponse(BaseModel):
    id: UUID
    name: str
    items: List[WatchlistItemResponse]

    class Config:
        from_attributes = True