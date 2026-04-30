from fastapi import APIRouter, Depends, status, Request
from app.services.user_service import UserService
from app.services.otp_service import OTPService
from app.services.auth_service import AuthService
from app.database.session import get_db
from app.schemas import (
    UserRegister, ForgotPassword, VerifyResetOTP, VerifyResetOTPResponse,
    ResetPassword, MessageResponse, BaseAPIResponse, ResendVerificationRequest
)

router = APIRouter()

async def get_user_service(db = Depends(get_db)):
    return UserService(db)

async def get_otp_service(db = Depends(get_db)):
    return OTPService(db)

async def get_auth_service(db = Depends(get_db)):
    return AuthService(db)

@router.post("/register", response_model=BaseAPIResponse[MessageResponse], status_code=status.HTTP_200_OK)
async def register(request: Request, data: UserRegister, svc: UserService = Depends(get_user_service)):
    """Register a new user."""
    result = await svc.register_user(data, request)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.post("/forgot-password", response_model=BaseAPIResponse[MessageResponse])
async def forgot_password(data: ForgotPassword, svc: OTPService = Depends(get_otp_service)):
    """Initiate password reset."""
    result = await svc.request_password_reset(data.email)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.post("/verify-reset-otp", response_model=BaseAPIResponse[VerifyResetOTPResponse])
async def verify_reset_otp(data: VerifyResetOTP, svc: OTPService = Depends(get_otp_service)):
    """Verify OTP and return reset token."""
    result = await svc.verify_reset_otp(data.email, data.otp)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.post("/reset-password", response_model=BaseAPIResponse[MessageResponse])
async def reset_password(data: ResetPassword, svc: AuthService = Depends(get_auth_service)):
    """Reset password using token."""
    result = await svc.reset_password_user(data)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.get("/verify-email")
async def verify_email(request: Request, token: str, svc: UserService = Depends(get_user_service)):
    """Verify email address."""
    result = await svc.verify_email(token, request)
    return BaseAPIResponse(success=True, message=result["message"], data=None)

@router.post("/resend-verification", response_model=BaseAPIResponse[MessageResponse])
async def resend_verification(request: Request, data: ResendVerificationRequest, svc: UserService = Depends(get_user_service)):
    """Resend verification email."""
    result = await svc.resend_verification(data, request)
    return BaseAPIResponse(success=True, message=result["message"], data=result)
