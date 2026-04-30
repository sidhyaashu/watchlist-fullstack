from pydantic import BaseModel
from datetime import datetime


class InstrumentResponse(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str
    last_price: float
    updated_at: datetime

    class Config:
        from_attributes = True