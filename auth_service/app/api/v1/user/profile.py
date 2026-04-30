from fastapi import APIRouter, Depends, Request
from app.services.user_service import UserService
from app.services.otp_service import OTPService
from app.database.session import get_db
from app.utils.security import get_current_user
from app.models import User
from app.schemas import (
    ChangePassword, MessageResponse, ProfileResponse, BaseAPIResponse,
    SetupPasswordVerifyOTP
)

router = APIRouter()

async def get_user_service(db = Depends(get_db)):
    return UserService(db)

async def get_otp_service(db = Depends(get_db)):
    return OTPService(db)

@router.post("/setup-password/request-otp", response_model=BaseAPIResponse[MessageResponse])
async def setup_password_request_otp(
    user: User = Depends(get_current_user),
    otp_svc: OTPService = Depends(get_otp_service)
):
    """Request OTP to setup local password for Google accounts."""
    result = await otp_svc.request_setup_password_otp(user)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.post("/setup-password/verify", response_model=BaseAPIResponse[MessageResponse])
async def setup_password_verify(
    request: Request,
    data: SetupPasswordVerifyOTP,
    user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service)
):
    """Verify OTP and set a local password for Google accounts."""
    result = await user_svc.setup_local_password(user, data.otp, data.new_password, request)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.get("/", response_model=BaseAPIResponse[ProfileResponse])
async def get_profile(
    user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service)
):
    """Get authenticated user's profile."""
    result = await user_svc.get_profile(user)
    return BaseAPIResponse(success=True, message="Profile retrieved successfully", data=result)

@router.post("/change-password", response_model=BaseAPIResponse[MessageResponse])
async def change_password(
    request: Request,
    data: ChangePassword,
    user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service)
):
    """Change user password."""
    result = await user_svc.change_password(user, data.current_password, data.new_password, request)
    return BaseAPIResponse(success=True, message=result["message"], data=result)

@router.delete("/", response_model=BaseAPIResponse[MessageResponse])
async def delete_account(
    request: Request,
    user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service)
):
    """Delete authenticated user's account."""
    result = await user_svc.delete_account(user, request)
    return BaseAPIResponse(success=True, message=result["message"], data=result)
