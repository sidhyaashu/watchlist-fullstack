from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("/", response_model=WatchlistResponse)
async def create_watchlist(
    payload: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        return await WatchlistService.create_watchlist(db, user_id, payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[WatchlistResponse])
async def get_watchlists(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    return await WatchlistService.get_user_watchlists(db, user_id, skip, limit)


@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    try:
        await WatchlistService.delete_watchlist(db, user_id, watchlist_id)
        return {"message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))