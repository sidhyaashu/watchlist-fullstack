from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from app.api.deps import get_current_user
from app.watchlist.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.watchlist.service.watchlist_service import WatchlistService
from app.watchlist.dependencies import get_watchlist_service

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("/", response_model=WatchlistResponse)
async def create_watchlist(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: str = Depends(get_current_user)
):
    try:
        return await service.create_watchlist(UUID(user_id) if isinstance(user_id, str) else user_id, payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[WatchlistResponse])
async def get_watchlists(
    skip: int = 0,
    limit: int = 20,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: str = Depends(get_current_user)
):
    return await service.get_user_watchlists(UUID(user_id) if isinstance(user_id, str) else user_id, skip, limit)


@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: UUID,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: str = Depends(get_current_user)
):
    try:
        await service.delete_watchlist(UUID(user_id) if isinstance(user_id, str) else user_id, watchlist_id)
        return {"message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))