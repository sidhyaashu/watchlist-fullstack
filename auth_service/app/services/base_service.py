from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis import get_redis

class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_redis_client(self):
        return await get_redis()
