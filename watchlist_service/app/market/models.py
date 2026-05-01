from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Numeric, PrimaryKeyConstraint
from app.db.base import Base


class CompanyMaster(Base):
    __tablename__ = "Company_Master"
    __table_args__ = {"schema": "public"}


    FINCODE = Column(Integer, primary_key=True, autoincrement=False)
    SCRIPCODE = Column(Integer)
    SCRIP_NAME = Column(String(35))
    SYMBOL = Column(String(20), index=True)
    COMPNAME = Column(String(255))
    industry = Column(String(100))
    ISIN = Column(String(20))


class NseMonthPrice(Base):
    __tablename__ = "Nse_Monthprice"  # Exact casing from Azure SQL

    Fincode = Column(Integer, primary_key=True, autoincrement=False)
    Month = Column(Integer, primary_key=True)
    Year = Column(Integer, primary_key=True)
    symbol = Column(String(25))
    Open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    Close = Column(Float)
    Volume = Column(Numeric)

    __table_args__ = (
        PrimaryKeyConstraint("Fincode", "Month", "Year"),
        {"schema": "public"}
    )


# Keep the local Instrument model for now if needed, but we'll mostly use the ones above
class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    exchange = Column(String)
    last_price = Column(Float)
    updated_at = Column(DateTime)