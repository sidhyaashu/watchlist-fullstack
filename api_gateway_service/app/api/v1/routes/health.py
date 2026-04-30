from fastapi import APIRouter
from app.repository.redis_repository import redis_client

router = APIRouter()


@router.get("/health", tags=["Monitoring"])
async def health_check():
    """Liveness + readiness check. Verifies Redis connectivity."""
    status = {"status": "healthy", "components": {}}

    try:
        await redis_client.ping()
        status["components"]["redis"] = "reachable"
    except Exception as e:
        status["components"]["redis"] = f"unreachable: {str(e)}"
        status["status"] = "degraded"

    if status["status"] != "healthy":
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content=status)

    return status