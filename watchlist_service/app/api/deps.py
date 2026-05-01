from uuid import UUID
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, MarketSessionLocal


# 🔹 DB Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🔹 External Market DB Dependency
async def get_market_db():
    async with MarketSessionLocal() as session:
        yield session


# 🔹 Auth Dependency
# The API Gateway's AuthMiddleware validates the JWT and injects the user identity
# as the X-User-ID header before forwarding requests to this service.
# We trust this header because the Watchlist Service is NOT exposed to the public internet —
# it only receives traffic from the gateway within the internal Docker network.
def get_current_user(request: Request) -> int:
    user_id = request.headers.get("X-User-ID")

    if not user_id:
        raise HTTPException(status_code=401, detail="Missing identity header")

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user identity")