from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.schemas.watchlist_item import (
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemReorder
)
from app.services.watchlist_item_service import WatchlistItemService

router = APIRouter(prefix="/watchlists/{watchlist_id}/items", tags=["Watchlist Items"])


@router.post("/", response_model=WatchlistItemResponse)
async def add_item(
    watchlist_id: UUID,
    payload: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        return await WatchlistItemService.add_item(db, user_id, watchlist_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[WatchlistItemResponse])
async def get_items(
    watchlist_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    return await WatchlistItemService.get_items(
        db, user_id, watchlist_id, skip, limit
    )


@router.delete("/{instrument_id}")
async def remove_item(
    watchlist_id: UUID,
    instrument_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        await WatchlistItemService.remove_item(
            db, user_id, watchlist_id, instrument_id
        )
        return {"message": "Removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/reorder")
async def reorder_items(
    watchlist_id: UUID,
    updates: list[WatchlistItemReorder],
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        await WatchlistItemService.reorder_items(
            db, user_id, watchlist_id, updates
        )
        return {"message": "Reordered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))