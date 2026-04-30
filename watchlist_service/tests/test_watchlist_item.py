import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.watchlist_item_service import WatchlistItemService
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException

@pytest.mark.asyncio
async def test_add_item_watchlist_not_found():
    db = AsyncMock()
    user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")

    # Mock repository to return None
    with MagicMock() as mock_repo:
        from app.repository.watchlist_repo import WatchlistRepository
        WatchlistRepository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundException) as excinfo:
            await WatchlistItemService.add_item(db, user_id, watchlist_id, data)
        
        assert "Watchlist not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_add_item_unauthorized():
    db = AsyncMock()
    user_id = uuid4()
    other_user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")
    
    watchlist = MagicMock()
    watchlist.user_id = other_user_id

    # Mock repository
    from app.repository.watchlist_repo import WatchlistRepository
    WatchlistRepository.get_by_id = AsyncMock(return_value=watchlist)
        
    with pytest.raises(UnauthorizedException):
        await WatchlistItemService.add_item(db, user_id, watchlist_id, data)

@pytest.mark.asyncio
async def test_add_item_limit_reached():
    db = AsyncMock()
    user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")
    
    watchlist = MagicMock()
    watchlist.user_id = user_id

    # Mock repository and service
    from app.repository.watchlist_repo import WatchlistRepository
    from app.repository.watchlist_item_repo import WatchlistItemRepository
    WatchlistRepository.get_by_id = AsyncMock(return_value=watchlist)
    WatchlistItemRepository.count_items = AsyncMock(return_value=WatchlistItemService.MAX_ITEMS)
        
    with pytest.raises(BadRequestException) as excinfo:
        await WatchlistItemService.add_item(db, user_id, watchlist_id, data)
    
    assert "Watchlist item limit reached" in str(excinfo.value)
