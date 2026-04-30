from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app.db.session import AsyncSessionLocal
from app.core.config import settings


# 🔹 DB Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# 🔹 Auth Dependency
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")