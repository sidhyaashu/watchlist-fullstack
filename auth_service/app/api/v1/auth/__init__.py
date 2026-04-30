from fastapi import APIRouter
from app.api.v1.auth.local import router as local_router
from app.api.v1.auth.session import router as session_router
from app.api.v1.auth.social import router as social_router

router = APIRouter()

router.include_router(local_router, tags=["Local Auth"])
router.include_router(session_router)
router.include_router(social_router)
