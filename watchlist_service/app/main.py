from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.watchlist.api.routes import api_router as watchlist_router
from app.core.exceptions import BaseAppException

app = FastAPI(title="Watchlist Service")

@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=exc.headers
    )

app.include_router(watchlist_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}