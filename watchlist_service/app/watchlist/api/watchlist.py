from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import JSONResponse
from uuid import UUID

from app.api.deps import get_current_user
from app.watchlist.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.watchlist.service.watchlist_service import WatchlistService
from app.watchlist.dependencies import get_watchlist_service
from app.core.error_handlers import handle_service_error
from app.core.http_cache import make_etag, cache_control_private, cache_control_no_store

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("", status_code=201)
async def create_watchlist(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: int = Depends(get_current_user),
):
    result = await handle_service_error(
        service.create_watchlist(user_id, payload.name)
    )
    return JSONResponse(
        content=result.model_dump(mode="json"),
        status_code=201,
        headers={"Cache-Control": cache_control_no_store()},
    )


@router.get("")
async def get_watchlists(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: int = Depends(get_current_user),
):
    results = await service.get_user_watchlists(user_id, skip, limit)
    data = [r.model_dump(mode="json") for r in results]
    etag = make_etag(data)

    # If the client already has this exact version, skip the body entirely
    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": cache_control_private(max_age=60),
            "ETag": etag,
        },
    )


@router.get("/{watchlist_id}")
async def get_watchlist(
    watchlist_id: UUID,
    request: Request,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: int = Depends(get_current_user),
):
    result = await handle_service_error(
        service.get_watchlist(user_id, watchlist_id)
    )
    data = result.model_dump(mode="json")
    etag = make_etag(data)

    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": cache_control_private(max_age=120),
            "ETag": etag,
        },
    )


@router.delete("/{watchlist_id}", status_code=204)
async def delete_watchlist(
    watchlist_id: UUID,
    service: WatchlistService = Depends(get_watchlist_service),
    user_id: int = Depends(get_current_user),
):
    await handle_service_error(
        service.delete_watchlist(user_id, watchlist_id)
    )
    return Response(
        status_code=204,
        headers={"Cache-Control": cache_control_no_store()},
    )