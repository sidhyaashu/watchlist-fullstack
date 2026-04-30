from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.repository.user_repository import get_user_by_id
from app.models import User

def validate_scope(required_scope: str):
    """
    Dependency to validate that the user has the required scope.
    The X-Scopes header is injected by the API Gateway after JWT validation.
    """
    def _validator(request: Request):
        # Gateway injects X-Scopes (e.g., "read,write,admin")
        user_scopes_str = request.headers.get("x-scopes", "")
        if not user_scopes_str:
            raise HTTPException(status_code=403, detail="Insufficient permissions: No scopes provided")
            
        user_scopes = [s.strip() for s in user_scopes_str.split(",")]
        
        if required_scope not in user_scopes:
            raise HTTPException(status_code=403, detail=f"Insufficient permissions: Requires '{required_scope}' scope")
            
    return _validator

def get_current_user_id(request: Request) -> int:
    """
    FastAPI dependency to extract the user_id from the Gateway-injected header.
    This trusts the X-User-ID header as the Gateway is the single point of entry.
    """
    user_id = request.headers.get("x-user-id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required: X-User-ID missing")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-ID format")

async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Returns the User model from the DB based on the Gateway-propagated ID.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
