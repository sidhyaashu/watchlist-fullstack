from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# 🔹 Create Watchlist Request
class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


# 🔹 Update Watchlist Request (future-ready)
class WatchlistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


# 🔹 Watchlist Response
class WatchlistResponse(BaseModel):
    id: UUID
    name: str
    is_default: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True