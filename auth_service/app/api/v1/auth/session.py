from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.database.session import get_db
from app.core.config import settings
from app.schemas import (
    UserLogin, TokenResponse, MessageResponse, BaseAPIResponse
)
from fastapi import HTTPException

router = APIRouter()
security = HTTPBearer()

async def get_auth_service(db = Depends(get_db)):
    return AuthService(db)

@router.post("/login", response_model=BaseAPIResponse[TokenResponse])
async def login(request: Request, response: Response, data: UserLogin, svc: AuthService = Depends(get_auth_service)):
    """Authenticate user and return access/refresh tokens."""
    result = await svc.login_user(data, request)
    
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return BaseAPIResponse(success=True, message="Login successful", data={"access_token": result["access_token"]})

@router.post("/refresh", response_model=BaseAPIResponse[TokenResponse])
async def refresh_token(request: Request, response: Response, svc: AuthService = Depends(get_auth_service)):
    """Refresh access token."""
    refresh_token_value = request.cookies.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        result = await svc.refresh_access_token(refresh_token_value)
        
        response.set_cookie(
            key="refresh_token",
            value=result["refresh_token"],
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="lax",
            path="/",
            max_age=7 * 24 * 60 * 60
        )
        
        return BaseAPIResponse(success=True, message="Token refreshed successfully", data={"access_token": result["access_token"]})
    except HTTPException as e:
        if e.status_code in [401, 403]:
            from fastapi.responses import JSONResponse
            error_res = JSONResponse(
                status_code=e.status_code,
                content={"success": False, "message": e.detail, "data": None}
            )
            error_res.delete_cookie(key="refresh_token", path="/")
            return error_res
        raise e
    except Exception as e:
        from fastapi.responses import JSONResponse
        error_res = JSONResponse(
            status_code=500,
            content={"success": False, "message": "An unexpected error occurred", "data": None}
        )
        error_res.delete_cookie(key="refresh_token", path="/")
        raise e

@router.post("/logout", response_model=BaseAPIResponse[MessageResponse])
async def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    svc: AuthService = Depends(get_auth_service)
):
    """Logout current session."""
    try:
        refresh_token_value = request.cookies.get("refresh_token")
        result = await svc.logout_user(credentials.credentials, refresh_token_value, request)
        
        response.delete_cookie(key="refresh_token", path="/")
        return BaseAPIResponse(success=True, message=result["message"], data=result)
    except Exception:
        # Always clear cookie even if backend revocation fails
        from fastapi.responses import JSONResponse
        res = JSONResponse(
            status_code=200, # Still return 200 because the client session is cleared
            content={"success": True, "message": "Logged out successfully", "data": None}
        )
        res.delete_cookie(key="refresh_token", path="/")
        return res

@router.post("/logout-all", response_model=BaseAPIResponse[MessageResponse])
async def logout_all(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    svc: AuthService = Depends(get_auth_service)
):
    """Logout from all devices."""
    user = await svc.validate_token_and_get_user(credentials.credentials)
    result = await svc.logout_all_user(user)
    return BaseAPIResponse(success=True, message=result["message"], data=result)
