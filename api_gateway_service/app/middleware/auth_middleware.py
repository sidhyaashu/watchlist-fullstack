from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse

from app.core.constants import PUBLIC_ROUTES
from app.services.auth_service import validate_jwt, validate_api_key
from app.repository.redis_repository import redis_client
import json


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        # ✅ Skip public routes (auth endpoints, health, etc.) or OPTIONS requests
        if request.method == "OPTIONS" or any(path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        payload = None

        try:
            # ✅ Try API key first
            api_payload = await validate_api_key(request)

            if api_payload:
                payload = api_payload
                request.state.auth_type = "API_KEY"
            else:
                # Fallback to JWT
                payload = await validate_jwt(request)
                request.state.auth_type = "JWT"

        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )

        # ✅ Store identity in request state — proxy will inject into downstream headers
        user_id = payload.get("sub") or payload.get("user_id")
        token_version = payload.get("token_version")

        # ✅ Ghost JWT Check: Verify status and version in Redis
        # This prevents banned users or invalidated sessions from continuing to use valid JWTs.
        cached_user = await redis_client.get(f"user_data:{user_id}")
        if cached_user:
            user_dict = json.loads(cached_user)
            if user_dict.get("status") != "active":
                return JSONResponse(status_code=403, content={"detail": "Account is inactive or banned"})
            if token_version is not None and user_dict.get("token_version") != token_version:
                return JSONResponse(status_code=401, content={"detail": "Session has been invalidated"})

        request.state.user_id = user_id
        request.state.scopes = payload.get("scope") or payload.get("scopes")

        return await call_next(request)