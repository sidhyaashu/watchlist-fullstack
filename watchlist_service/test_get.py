import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import uuid

DATABASE_URL = "postgresql+asyncpg://InvestKode:Xpolog%4000%26@finglobalai-data-dum.postgres.database.azure.com:5432/financial_db?ssl=require"

async def test_get():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # This is essentially what WatchlistItemRepository.get_items does
        query = text("""
            SELECT 
                wi.symbol, 
                cm.compname, 
                mp.close as last_price,
                eq.mcap
            FROM app.watchlist_items wi
            LEFT JOIN public.company_master cm ON wi.instrument_id = cm.fincode
            LEFT JOIN (
                SELECT fincode, MAX(year * 100 + month) as latest_period
                FROM public.nse_monthprice
                GROUP BY fincode
            ) lp ON wi.instrument_id = lp.fincode
            LEFT JOIN public.nse_monthprice mp ON wi.instrument_id = mp.fincode AND (mp.year * 100 + mp.month) = lp.latest_period
            LEFT JOIN public.company_equity eq ON wi.instrument_id = eq.fincode
        """)
        
        res = await session.execute(query)
        for row in res:
            print(f"SYMBOL: {row[0]}, NAME: {row[1]}, PRICE: {row[2]}, MCAP: {row[3]}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_get())
