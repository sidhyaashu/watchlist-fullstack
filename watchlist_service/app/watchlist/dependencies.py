from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

from app.watchlist.repository.watchlist_repo import WatchlistRepository
from app.watchlist.repository.watchlist_item_repo import WatchlistItemRepository
from app.watchlist.service.watchlist_service import WatchlistService
from app.watchlist.service.watchlist_item_service import WatchlistItemService


def get_watchlist_repository(db: AsyncSession = Depends(get_db)) -> WatchlistRepository:
    return WatchlistRepository(db)

def get_watchlist_item_repository(db: AsyncSession = Depends(get_db)) -> WatchlistItemRepository:
    return WatchlistItemRepository(db)


def get_watchlist_service(
    repo: WatchlistRepository = Depends(get_watchlist_repository),
    item_repo: WatchlistItemRepository = Depends(get_watchlist_item_repository)
) -> WatchlistService:
    return WatchlistService(repo, item_repo)


def get_watchlist_item_service(

    repo: WatchlistItemRepository = Depends(get_watchlist_item_repository),
    watchlist_repo: WatchlistRepository = Depends(get_watchlist_repository)
) -> WatchlistItemService:
    return WatchlistItemService(repo, watchlist_repo)

