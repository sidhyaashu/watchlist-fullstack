import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import uuid

DATABASE_URL = "postgresql+asyncpg://InvestKode:Xpolog%4000%26@finglobalai-data-dum.postgres.database.azure.com:5432/financial_db?ssl=require"

async def test_add():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Get a user or watchlist
        w_query = text("SELECT id FROM app.watchlists LIMIT 1")
        w_res = await session.execute(w_query)
        w_id = w_res.scalar()
        
        if not w_id:
            print("No watchlist found. Creating one for user 1...")
            w_id = uuid.uuid4()
            await session.execute(text("INSERT INTO app.watchlists (id, user_id, name) VALUES (:id, 1, 'Main')"), {"id": w_id})
        
        print(f"Adding item to watchlist {w_id}...")
        # Add ABB (FINCODE 100002)
        await session.execute(
            text("INSERT INTO app.watchlist_items (id, watchlist_id, instrument_id, symbol, exchange, position) VALUES (:id, :w_id, 100002, 'ABB', 'NSE', 1)"),
            {"id": uuid.uuid4(), "w_id": w_id}
        )
        await session.commit()
        print("Item added successfully!")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_add())
