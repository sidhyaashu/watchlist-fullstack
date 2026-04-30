import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings

from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.middleware.ai_logging_middleware import AILoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize a global connection-pooled client for proxying requests.
    # We use a 300s timeout to match the Nginx proxy_read_timeout.
    client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200),
        timeout=300.0,
    )
    app.state.client = client
    yield
    await client.aclose()


app = FastAPI(title="InvestCode API Gateway", lifespan=lifespan)

import logging
logger = logging.getLogger(__name__)

@app.exception_handler(httpx.HTTPError)
async def httpx_exception_handler(request: Request, exc: httpx.HTTPError):
    # If the downstream microservice connection fails, log it and return a 502 Bad Gateway
    logger.error(f"Downstream service error during proxy: {exc}", exc_info=True)
    return JSONResponse(
        status_code=502,
        content={"success": False, "message": "Downstream service unavailable", "data": None}
    )

# ─── Middleware Stack (ORDER MATTERS — last added runs first) ─────────────────
app.add_middleware(RequestIDMiddleware)   # 1. Assign request ID
app.add_middleware(LoggingMiddleware)     # 2. Log every request
app.add_middleware(AILoggingMiddleware)   # 3. Log AI-specific metadata
app.add_middleware(AuthMiddleware)        # 4. Authenticate & inject identity
app.add_middleware(RateLimitMiddleware)   # 5. Enforce rate limits

# CORS must be last (outermost) to ensure headers are added to all error responses
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.CLIENT_URL,        # e.g. http://localhost:3000
        "http://localhost:3000",    # local dev fallback
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-User-ID"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")