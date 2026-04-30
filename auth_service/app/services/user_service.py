import hashlib
import logging
import jwt
import json
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.services.analytics_service import AnalyticsService
from app.models import User, UserStatusEnum, AuthProviderEnum, OTPTypeEnum
from app.repository.user_repository import get_user_by_email, get_user_by_id, get_user_by_phone
from app.repository.otp_repository import create_otp, get_valid_otp, mark_otp_used
from app.core.security import hash_password
from app.services.token_service import create_email_verification_token
from app.utils.email_utils import send_verification_email_async
from app.core.config import settings
from app.core.security import verify_password


logger = logging.getLogger(__name__)

class UserService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.analytics = AnalyticsService(db)


    async def get_profile(self, user: User):
        redis = await self.get_redis_client()
        cache_key = f"user_profile:{user.id}"
        
        if redis:
            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)
        
        profile = {
            "user_id": user.id, 
            "email": user.email, 
            "name": user.name, 
            "phone": user.phone
        }
        
        if redis:
            await redis.setex(cache_key, 600, json.dumps(profile))
        
        return profile

    async def register_user(self, user_data, request: Request):
        user_data.email = user_data.email.lower()
        print(f"DEBUG: Registering user {user_data.email}")
        existing_user = await get_user_by_email(self.db, user_data.email)
        if existing_user:
            # Handle existing user based on state
            if not existing_user.is_verified:
                # Resend verification email
                await self.resend_verification(user_data, request)
                return {"message": "Verification link has been resent to your email."}
            
            if existing_user.auth_provider == AuthProviderEnum.GOOGLE:
                raise HTTPException(
                    status_code=400, 
                    detail="This account was created with Google. Please log in with Google or use 'Forgot Password' to set a password."
                )
            
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        if await get_user_by_phone(self.db, user_data.phone):
            raise HTTPException(status_code=400, detail="An account with this phone number already exists.")

        hashed = hash_password(user_data.password)

        new_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hashed,
            dob=user_data.dob,
            is_verified=False,
            auth_provider=AuthProviderEnum.LOCAL,
            status=UserStatusEnum.ACTIVE,
        )

        self.db.add(new_user)
        await self.db.flush()

        token = create_email_verification_token(new_user)
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        # Create record in OTPCode table instead of User table
        await create_otp(
            self.db, 
            new_user.id, 
            hashed_token, 
            OTPTypeEnum.EMAIL_VERIFY,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES
        )

        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Registration failed during database commit: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Registration failed due to an internal error. Please try again later."
            )

        # Track Analytics
        try:
            await self.analytics.track_registration(new_user.id, request)
        except Exception as e:
            logger.warning(f"Failed to track registration analytics: {e}")

        # Send Email
        try:
            await send_verification_email_async(new_user.email, token)
        except Exception as e:
            logger.critical(f"Registration succeeded but email dispatch failed: {e}")
            return {"message": "Registration successful! We experienced a delay sending your verification email. Please check your inbox shortly or use 'Resend Verification'."}

        return {"message": "Registration successful! Please check your email for a verification link."}

    async def change_password(self, user: User, current_password, new_password, request: Request):
        
        
        if user.auth_provider not in [AuthProviderEnum.LOCAL, AuthProviderEnum.BOTH]:
            raise HTTPException(status_code=400, detail="Password change is not available for this account type.")
            
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.token_version += 1
        await self.db.commit()

        # Analytics
        await self.analytics.track_password_change(user.id, request)

        # Invalidate cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_status:{user.id}")
            await redis.delete(f"user_profile:{user.id}")

        return {"message": "Password changed successfully"}

    async def delete_account(self, user: User, request: Request):
        user.status = UserStatusEnum.INACTIVE
        await self.db.commit()
        
        # Invalidate cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_status:{user.id}")
            await redis.delete(f"user_profile:{user.id}")
            
        # Analytics
        await self.analytics.track_account_delete(user.id, request)
        
        return {"message": "Account deleted successfully"}
    
    async def resend_verification(self, data, request: Request):
        data.email = data.email.lower()
        print(f"DEBUG: Resending verification to {data.email}")
        user = await get_user_by_email(self.db, data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User with this email not found.")

        if user.is_verified:
            if user.auth_provider == AuthProviderEnum.GOOGLE:
                return {"message": "Your email is already verified via Google."}
            return {"message": "Your email is already verified. You can login."}

        token = create_email_verification_token(user)
        hashed_token = hashlib.sha256(token.encode()).hexdigest()

        # Create record in OTPCode table instead of User table
        await create_otp(
            self.db, 
            user.id, 
            hashed_token, 
            OTPTypeEnum.EMAIL_VERIFY,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES
        )

        await self.db.commit()

        try:
            await send_verification_email_async(user.email, token)
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to send verification email. Please try again later.")

        return {"message": "Verification link has been sent."}

    async def verify_email(self, token: str, request: Request):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.PyJWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await get_user_by_id(self.db, payload.get("user_id"))
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
            
        if user.is_verified:
            return {"message": "Email already verified"}

        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        
        # Validate against NEW OTPCode table
        db_otp = await get_valid_otp(
            self.db, 
            user.id, 
            hashed_token, 
            OTPTypeEnum.EMAIL_VERIFY
        )

        if not db_otp:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user.is_verified = True
        
        # Mark as used
        await mark_otp_used(self.db, db_otp)
        
        await self.db.commit()

        # Analytics
        await self.analytics.track_profile_update(user.id, request)
        
        # Invalidate status cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_status:{user.id}")

        return {"message": "Email verified successfully"}

    async def setup_local_password(self, user: User, otp: str, new_password: str, request: Request):
        if user.auth_provider != AuthProviderEnum.GOOGLE:
            raise HTTPException(status_code=400, detail="This account already has a password set.")

        hashed_input_otp = hashlib.sha256(otp.encode()).hexdigest()

        db_otp = await get_valid_otp(
            self.db, 
            user.id, 
            hashed_input_otp, 
            OTPTypeEnum.SETUP_PASSWORD
        )

        if not db_otp:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        # Mark as used
        await mark_otp_used(self.db, db_otp)

        user.password_hash = hash_password(new_password)
        user.auth_provider = AuthProviderEnum.BOTH
        user.token_version += 1
        await self.db.commit()

        # Analytics
        await self.analytics.track_password_change(user.id, request)

        # Invalidate cache
        redis = await self.get_redis_client()
        if redis:
            await redis.delete(f"user_data:{user.id}")
            await redis.delete(f"user_status:{user.id}")
            await redis.delete(f"user_profile:{user.id}")

        return {"message": "Password setup successfully. You can now login using either Google or your password."}
