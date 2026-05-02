from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.watchlist.api.routes import api_router as watchlist_router
from app.market.api.routes import api_router as market_router
from app.core.exceptions import BaseAppException

from app.utils.logger import logger

app = FastAPI(title="Watchlist Service", redirect_slashes=False)


# ─── Exception Handlers ───────────────────────────────────────────────────────

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """Maps domain exceptions (400/401/403/404) to clean JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for any unhandled exception.
    Returns a safe 500 without leaking stack traces to the client.
    The full exception is logged for debugging.
    """
    logger.error(
        "[unhandled_exception]",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

app.include_router(watchlist_router, prefix="/api/v1")

app.include_router(market_router, prefix="/api/v1")



@app.get("/health")
async def health():
    """Health check — also reports Redis circuit breaker state for ops visibility."""
    from app.core.circuit_breaker import redis_circuit_breaker
    return {
        "status": "ok",
        "redis_circuit": redis_circuit_breaker.state,
    }