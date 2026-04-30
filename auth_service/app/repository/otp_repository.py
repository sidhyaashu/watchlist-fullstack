import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import OTPCode, OTPTypeEnum

async def create_otp(db: AsyncSession, user_id: int, code_hash: str, otp_type: OTPTypeEnum, expiry_minutes: int = 10):
    # Security: Invalidate any existing valid OTPs of this type for this user
    await invalidate_old_otps(db, user_id, otp_type)

    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiry_minutes)
    otp = OTPCode(
        user_id=user_id,
        code_hash=code_hash,
        otp_type=otp_type,
        expires_at=expires_at
    )
    db.add(otp)
    await db.commit()
    return otp

async def get_valid_otp(db: AsyncSession, user_id: int, code_hash: str, otp_type: OTPTypeEnum):
    query = select(OTPCode).where(
        OTPCode.user_id == user_id,
        OTPCode.code_hash == code_hash,
        OTPCode.otp_type == otp_type,
        OTPCode.is_used == False,
        OTPCode.expires_at > datetime.datetime.now(datetime.timezone.utc)
    ).order_by(OTPCode.created_at.desc())
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def mark_otp_used(db: AsyncSession, otp: OTPCode):
    otp.is_used = True
    await db.commit()

async def invalidate_old_otps(db: AsyncSession, user_id: int, otp_type: OTPTypeEnum):
    """Mark all pending valid OTPs of a specific type as used/invalid for a user."""
    from sqlalchemy import update
    query = update(OTPCode).where(
        OTPCode.user_id == user_id,
        OTPCode.otp_type == otp_type,
        OTPCode.is_used == False,
        OTPCode.expires_at > datetime.datetime.now(datetime.timezone.utc)
    ).values(is_used=True)
    
    await db.execute(query)
    await db.commit()
