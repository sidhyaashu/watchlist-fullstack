from fastapi import APIRouter

from app.watchlist.api.watchlist import router as watchlist_router
from app.watchlist.api.watchlist_item import router as watchlist_item_router

api_router = APIRouter()

api_router.include_router(watchlist_router)
api_router.include_router(watchlist_item_router)
