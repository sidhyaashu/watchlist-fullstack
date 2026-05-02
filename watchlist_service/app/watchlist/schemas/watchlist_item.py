from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime



# 🔹 Add Instrument to Watchlist
class WatchlistItemCreate(BaseModel):
    instrument_id: int = Field(...)
    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: str = Field(..., min_length=1, max_length=10)


# 🔹 Update Position (ordering)
class WatchlistItemReorder(BaseModel):
    instrument_id: int
    position: int


# 🔹 Response Model
class WatchlistItemResponse(BaseModel):
    id: UUID
    instrument_id: int
    symbol: str
    exchange: str
    position: Optional[int]
    added_at: Optional[datetime]

    # Enrichment fields (from Azure market tables)
    name: Optional[str] = None
    last_price: Optional[float] = None
    change_percent: Optional[float] = None
    sector: Optional[str] = None
    year_high: Optional[float] = None
    year_low: Optional[float] = None
    mcap: Optional[float] = None
    pe: Optional[float] = None



    class Config:
        from_attributes = True

class PaginatedWatchlistItems(BaseModel):
    items: List[WatchlistItemResponse]
    total: int
    skip: int
    limit: int


class BulkAddItems(BaseModel):
    items: list[WatchlistItemCreate]


class WatchlistDetailResponse(BaseModel):
    id: UUID
    name: str
    items: List[WatchlistItemResponse]

    class Config:
        from_attributes = True