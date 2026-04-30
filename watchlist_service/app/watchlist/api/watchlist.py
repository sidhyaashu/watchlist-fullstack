from fastapi import APIRouter, Depends, Query
from uuid import UUID

from app.api.deps import get_current_user
from app.watchlist.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.watchlist.service.watchlist_service import WatchlistService
from app.watchlist.dependencies import get_watchlist_service
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.error_handlers import handle_service_error

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("/", response_model=WatchlistResponse, status_code=201)
async def create_watchlist(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: UUID = Depends(get_current_user),
):
    return await handle_service_error(
        service.create_watchlist(user_id, payload.name)
    )


@router.get("/", response_model=list[WatchlistResponse])
async def get_watchlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: UUID = Depends(get_current_user),
):
    return await service.get_user_watchlists(user_id, skip, limit)


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: UUID,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: UUID = Depends(get_current_user),
):
    return await handle_service_error(
        service.get_watchlist(user_id, watchlist_id)
    )


@router.delete("/{watchlist_id}", status_code=204)
async def delete_watchlist(
    watchlist_id: UUID,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: UUID = Depends(get_current_user),
):
    return await handle_service_error(
        service.delete_watchlist(user_id, watchlist_id)
    )