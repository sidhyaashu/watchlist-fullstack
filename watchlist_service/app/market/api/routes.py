from fastapi import APIRouter
from app.market.api import market

api_router = APIRouter()
api_router.include_router(market.router, prefix="/market", tags=["market"])
