from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.base import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    exchange = Column(String)
    last_price = Column(Float)
    updated_at = Column(DateTime)