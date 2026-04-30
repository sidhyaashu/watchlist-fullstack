from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.api.deps import get_current_user
from app.watchlist.schemas.watchlist_item import (
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemReorder
)
from app.watchlist.service.watchlist_item_service import WatchlistItemService
from app.watchlist.dependencies import get_watchlist_item_service

router = APIRouter(prefix="/watchlists/{watchlist_id}/items", tags=["Watchlist Items"])


@router.post("/", response_model=WatchlistItemResponse)
async def add_item(
    watchlist_id: UUID,
    payload: WatchlistItemCreate,
    service: WatchlistItemService = Depends(get_watchlist_item_service),
    user_id: str = Depends(get_current_user)
):
    try:
        return await service.add_item(UUID(user_id) if isinstance(user_id, str) else user_id, watchlist_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[WatchlistItemResponse])
async def get_items(
    watchlist_id: UUID,
    skip: int = 0,
    limit: int = 50,
    service: WatchlistItemService = Depends(get_watchlist_item_service),
    user_id: str = Depends(get_current_user)
):
    return await service.get_items(
        UUID(user_id) if isinstance(user_id, str) else user_id, watchlist_id, skip, limit
    )


@router.delete("/{instrument_id}")
async def remove_item(
    watchlist_id: UUID,
    instrument_id: str,
    service: WatchlistItemService = Depends(get_watchlist_item_service),
    user_id: str = Depends(get_current_user)
):
    try:
        await service.remove_item(
            UUID(user_id) if isinstance(user_id, str) else user_id, watchlist_id, instrument_id
        )
        return {"message": "Removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/reorder")
async def reorder_items(
    watchlist_id: UUID,
    updates: list[WatchlistItemReorder],
    service: WatchlistItemService = Depends(get_watchlist_item_service),
    user_id: str = Depends(get_current_user)
):
    try:
        await service.reorder_items(
            UUID(user_id) if isinstance(user_id, str) else user_id, watchlist_id, updates
        )
        return {"message": "Reordered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))