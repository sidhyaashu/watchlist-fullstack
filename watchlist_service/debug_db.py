import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://InvestKode:Xpolog%4000%26@finglobalai-data-dum.postgres.database.azure.com:5432/financial_db?ssl=require"

async def debug():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("--- Checking Columns in 'public.company_equity' ---")
        cols_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'company_equity'
        """)
        cols = await session.execute(cols_query)
        for c in cols:
            print(f"Column: {c[0]}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(debug())
