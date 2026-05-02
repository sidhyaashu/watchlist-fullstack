import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check():
    url = os.environ["DATABASE_URL"]
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        print("--- Checking 'public' schema ---")
        r = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        rows = r.fetchall()
        if rows:
            print("Tables in 'public' schema:")
            for row in rows:
                print(f"  - {row[0]}")
        else:
            print("NO TABLES FOUND in 'public' schema!")
            
    await engine.dispose()

asyncio.run(check())
