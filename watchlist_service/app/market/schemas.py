from pydantic import BaseModel


from typing import Optional

class InstrumentResponse(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str
    last_price: Optional[float] = None
    mcap: Optional[float] = None
    pe: Optional[float] = None



    class Config:
        from_attributes = True