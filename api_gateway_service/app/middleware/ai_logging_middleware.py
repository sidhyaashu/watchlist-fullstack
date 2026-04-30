import time
import json
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class AILoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        if not path.startswith("/api/v1/ai"):
            return await call_next(request)

        start_time = time.time()

        response = await call_next(request)

        latency = time.time() - start_time

        log_data = {
            "type": "AI_REQUEST",
            "user_id": getattr(request.state, "user_id", None),
            "endpoint": path,
            "latency_ms": round(latency * 1000, 2),
        }

        print(json.dumps(log_data))

        return response