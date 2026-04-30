from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException

from app.repository.redis_repository import increment, get_ttl
from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        ip = request.client.host
        user_id = getattr(request.state, "user_id", None)

        # 🔑 Determine key
        if path.startswith("/api/v1/ai"):
            key = f"rate_limit:ai:{user_id or ip}"
            limit = settings.RATE_LIMIT_AI

        elif user_id:
            key = f"rate_limit:user:{user_id}"
            limit = settings.RATE_LIMIT_USER

        else:
            key = f"rate_limit:ip:{ip}"
            limit = settings.RATE_LIMIT_IP

        import logging
        logger = logging.getLogger(__name__)

        try:
            count = await increment(key)

            if count > limit:
                ttl = await get_ttl(key)
                from starlette.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests"},
                    headers={"Retry-After": str(ttl)}
                )
        except Exception as e:
            # Fail-open if Redis is down
            logger.error(f"Rate Limiting Redis Error: {e}")

        return await call_next(request)