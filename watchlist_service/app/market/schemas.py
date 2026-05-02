from pydantic import BaseModel


class InstrumentResponse(BaseModel):
    id: int
    symbol: str
    name: str
    last_price: float

    class Config:
        from_attributes = True