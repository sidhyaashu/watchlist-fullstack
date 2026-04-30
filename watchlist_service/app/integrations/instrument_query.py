from sqlalchemy import Table, Column, String, Float, MetaData
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# 🔹 Define minimal model for read-only enrichment
metadata = MetaData()

Instrument = Table(
    "instruments",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String),
    Column("last_price", Float),
    Column("change_percent", Float),
)

# assume instruments table exists


class InstrumentQuery:

    @staticmethod
    async def get_by_id(db: AsyncSession, instrument_id: str):
        result = await db.execute(
            select(Instrument).where(Instrument.c.id == instrument_id)
        )
        return result.first()

    @staticmethod
    async def bulk_get(db: AsyncSession, instrument_ids: list[str]):
        result = await db.execute(
            select(Instrument).where(Instrument.c.id.in_(instrument_ids))
        )
        return result.fetchall()