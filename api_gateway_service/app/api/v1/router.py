from fastapi import APIRouter
from app.api.v1.routes import health, proxy

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(proxy.router, tags=["Proxy"])