import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        for table in ["company_master", "nse_monthprice"]:
            print(f"--- Columns for {table} ---")
            r = await conn.execute(text(
                f"SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '{table}'"
            ))
            rows = r.fetchall()
            for row in rows:
                print(f"  - {row[0]}")
            print("\n")
            
    await engine.dispose()

asyncio.run(check())
