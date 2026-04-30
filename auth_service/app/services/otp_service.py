import secrets
import hashlib
import logging
from fastapi import HTTPException
from app.services.base_service import BaseService
from app.repository.user_repository import get_user_by_email
from app.repository.otp_repository import create_otp, get_valid_otp, mark_otp_used
from app.utils.email_utils import send_email_otp
from app.models import OTPTypeEnum
from app.models.enums import AuthProviderEnum
from app.services.token_service import create_reset_token


logger = logging.getLogger(__name__)

class OTPService(BaseService):
    async def request_password_reset(self, email: str):
        user = await get_user_by_email(self.db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User with this email not found.")

        # Allow Google users to get an OTP to set their first password
        otp = str(secrets.randbelow(900000) + 100000)
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

        # Create record in new table
        await create_otp(
            self.db, 
            user.id, 
            hashed_otp, 
            OTPTypeEnum.PASSWORD_RESET,
            expiry_minutes=10
        )

        try:
            await send_email_otp(email, otp)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again later.")

        return {"message": "OTP has been sent to your email."}

    async def verify_reset_otp(self, email: str, otp: str):
        user = await get_user_by_email(self.db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired OTP")

        hashed_input_otp = hashlib.sha256(otp.encode()).hexdigest()

        # Check new table
        db_otp = await get_valid_otp(
            self.db, 
            user.id, 
            hashed_input_otp, 
            OTPTypeEnum.PASSWORD_RESET
        )

        if not db_otp:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")

        # Mark as used
        await mark_otp_used(self.db, db_otp)

        reset_token = create_reset_token(user)
        return {"message": "OTP verified", "reset_token": reset_token}
    
    async def request_email_verification(self, user):
        # Implementation for generating verification token using the new table
        otp = str(secrets.randbelow(900000) + 100000)
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

        await create_otp(
            self.db, 
            user.id, 
            hashed_otp, 
            OTPTypeEnum.EMAIL_VERIFY,
            expiry_minutes=30
        )
        return otp

    async def request_setup_password_otp(self, user):
        
        if user.auth_provider != AuthProviderEnum.GOOGLE:
            raise HTTPException(status_code=400, detail="This account already has a password set.")

        otp = str(secrets.randbelow(900000) + 100000)
        hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

        await create_otp(
            self.db, 
            user.id, 
            hashed_otp, 
            OTPTypeEnum.SETUP_PASSWORD,
            expiry_minutes=15
        )

        try:
            await send_email_otp(user.email, otp)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise HTTPException(status_code=500, detail="Failed to send OTP email. Please try again later.")

        return {"message": "An OTP has been sent to your registered email."}
