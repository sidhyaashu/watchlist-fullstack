import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models import RefreshToken
from app.core.config import settings

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_phone(db: AsyncSession, phone: str) -> User:
    query = select(User).where(User.phone == phone)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def store_refresh_token(db: AsyncSession, user_id: int, token: str) -> RefreshToken:
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires
    )

    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)

    return refresh_token

async def get_refresh_token(db: AsyncSession, token: str):
    query = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.execute(query)
    return result.scalars().first()

async def revoke_refresh_token(db: AsyncSession, token: str):
    if not token:
        return
    query = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.execute(query)
    db_tokens = result.scalars().all()

    if db_tokens:
        for db_token in db_tokens:
            db_token.is_revoked = True
        await db.commit()

