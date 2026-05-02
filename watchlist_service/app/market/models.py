from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Numeric, PrimaryKeyConstraint
from app.db.base import Base


class CompanyMaster(Base):
    __tablename__ = "company_master"
    __table_args__ = {"schema": "public"}

    fincode = Column(Integer, primary_key=True, autoincrement=False)
    scripcode = Column(Integer)
    scrip_name = Column(String(35))
    symbol = Column(String(20), index=True)
    compname = Column(String(255))
    industry = Column(String(100))
    isin = Column(String(20))


class NseMonthPrice(Base):
    __tablename__ = "nse_monthprice"

    fincode = Column(Integer, primary_key=True, autoincrement=False)
    month = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    symbol = Column(String(25))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Numeric)

    __table_args__ = (
        PrimaryKeyConstraint("fincode", "month", "year"),
        {"schema": "public"}
    )


class CompanyEquity(Base):
    __tablename__ = "company_equity"
    __table_args__ = {"schema": "public"}

    FINCODE = Column(Integer, primary_key=True, autoincrement=False)