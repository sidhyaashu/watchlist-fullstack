import logging
import smtplib
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


from app.api.v1 import router as api_v1
from app.database.session import get_db
from app.core.config import settings
from app.core.redis import redis_client, get_redis

# ------------------ LOGGING ------------------
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------ LIFESPAN ------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Service starting up...")
    logger.info(f"Allowed CORS Origins: {settings.ALLOWED_HOSTS}")
    await redis_client.connect()
    yield
    # Shutdown
    logger.info("Service shutting down...")
    await redis_client.disconnect()

# ------------------ APP INITIALIZATION ------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# ------------------ CUSTOM MIDDLEWARE ------------------
@app.middleware("http")
async def proxy_headers_middleware(request: Request, call_next):
    # Unpack proxy headers correctly since Uvicorn's --proxy-headers handles For/Proto but not Host.
    host = request.headers.get("x-forwarded-host")
    proto = request.headers.get("x-forwarded-proto")
    
    if host and "auth_service" not in host:
        parts = host.split(":")
        server_port = int(parts[1]) if len(parts) == 2 else (443 if proto == "https" else 80)
        request.scope["server"] = (parts[0], server_port)
        
        # Rewrite host header for URL generation (e.g. request.url_for)
        headers = [(b"host", host.encode()) if k == b"host" else (k, v) for k, v in request.scope["headers"]]
        request.scope["headers"] = headers
        
    if proto:
        request.scope["scheme"] = proto

    try:
        response = await call_next(request)
        if response.status_code == 400:
            logger.warning(f"400 Bad Request: Path={request.url.path} Method={request.method} Headers={dict(request.headers)}")
        return response
    except Exception as exc:
        logger.error(f"Unhandled error caught in middleware: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "An internal server error occurred.", "data": None}
        )

# ------------------ CORS MIDDLEWARE ------------------
# Removed: The API Gateway exclusively handles CORS for all incoming requests.

# ------------------ SESSION MIDDLEWARE ------------------
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# Legacy handlers (kept for FastAPI-specific exceptions like 422)
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request, exc):
    logger.error("Database error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Database operation failed.", "data": None}
    )
 
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None}
    )
 
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "success": False, 
            "message": "Validation error", 
            "data": {"errors": exc.errors()}
        })
    )

# ------------------ MONITORING ------------------
@app.get("/health", tags=["Monitoring"])
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """Deep health check for API and dependencies."""
    status = {"status": "healthy", "components": {}}
    
    # DB
    try:
        await db.execute(text("SELECT 1"))
        status["components"]["database"] = "reachable"
    except Exception as e:
        status["components"]["database"] = f"unreachable: {str(e)}"
        status["status"] = "degraded"

    # Redis
    try:
        if redis:
            await redis.ping()
            status["components"]["redis"] = "reachable"
        else:
            status["components"]["redis"] = "not_initialized"
            status["status"] = "degraded"
    except Exception as e:
        status["components"]["redis"] = f"unreachable: {str(e)}"
        status["status"] = "degraded"

    # SMTP
    def check_smtp():
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=5) as server:
            server.starttls()
            server.noop()

    try:
        if settings.SMTP_SERVER:
            await run_in_threadpool(check_smtp)
            status["components"]["smtp"] = "reachable"
        else:
            status["components"]["smtp"] = "not_configured"
    except Exception as e:
        status["components"]["smtp"] = f"error: {str(e)}"
        status["status"] = "degraded"

    if status["status"] != "healthy":
        return JSONResponse(status_code=503, content=status)
    return status

app.include_router(api_v1, prefix="/api/v1")
