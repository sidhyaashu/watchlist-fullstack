from fastapi import Request, HTTPException
from app.core.security import decode_jwt
from app.repository.api_key_repository import lookup_api_key


async def validate_jwt(request: Request) -> dict:
    """Extract and locally validate a JWT from the Authorization header."""
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed token")

    token = auth_header.split(" ")[1]
    payload = decode_jwt(token)
    return payload


async def validate_api_key(request: Request) -> dict | None:
    """
    Extract and validate an API key from the X-API-Key header.
    Looks up the key in Redis. Returns None if header is absent.
    Raises 403 if header is present but key is invalid/inactive.
    """
    raw_key = request.headers.get("x-api-key")

    if not raw_key:
        return None

    payload = await lookup_api_key(raw_key)

    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key")

    return payload