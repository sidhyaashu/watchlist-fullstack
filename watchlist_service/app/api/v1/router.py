from fastapi import APIRouter

from app.api.v1.endpoints import watchlist, watchlist_item

api_router = APIRouter()

api_router.include_router(watchlist.router)
api_router.include_router(watchlist_item.router)