from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.services.auth_service import AuthService
from app.database.session import get_db

router = APIRouter()

async def get_auth_service(db = Depends(get_db)):
    return AuthService(db)

@router.get("/google/login", tags=["OAuth"])
async def google_login(request: Request, svc: AuthService = Depends(get_auth_service)):
    """Initiate Google login."""
    return await svc.google_login_user(request)

@router.get("/google/callback", tags=["OAuth"])
async def google_callback(request: Request, svc: AuthService = Depends(get_auth_service)):
    """Handle Google callback."""
    frontend_url = settings.FRONTEND_URL
    try:
        result = await svc.google_callback_user(request)
    except HTTPException as e:
        if "Mismatched provider" in str(e.detail):
            return RedirectResponse(f"{frontend_url}/login?error=mismatched_provider")
        elif "Account is inactive or banned" in str(e.detail):
            return RedirectResponse(f"{frontend_url}/login?error=account_banned")
        return RedirectResponse(f"{frontend_url}/login?error=auth_failed")
    
    
    # Check if result is a Pydantic model or dict
    access = getattr(result, "access_token", getattr(result, "access", None))
    refresh = getattr(result, "refresh_token", getattr(result, "refresh", None))
    
    if hasattr(result, "get") and access is None:
        access = result.get("access_token") or result.get("access")
        refresh = result.get("refresh_token") or result.get("refresh")
        
    if access:
        response = RedirectResponse(f"{frontend_url}/auth/callback?success=true")
        if refresh:
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=settings.ENVIRONMENT == "production",  # False in dev (HTTP)
                samesite="lax",
                path="/",
                max_age=7 * 24 * 60 * 60
            )
        return response
    
    return RedirectResponse(f"{frontend_url}/login?error=auth_failed")
