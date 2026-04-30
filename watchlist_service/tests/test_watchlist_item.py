import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.watchlist.service.watchlist_item_service import WatchlistItemService
from app.core.exceptions import UnauthorizedException, NotFoundException, BadRequestException

@pytest.fixture
def service():
    repo = AsyncMock()
    watchlist_repo = AsyncMock()
    market_service = AsyncMock()
    return WatchlistItemService(repo, watchlist_repo, market_service)

@pytest.mark.asyncio
async def test_add_item_watchlist_not_found(service):
    user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")

    service.watchlist_repo.get_by_id.return_value = None
    
    with pytest.raises(NotFoundException) as excinfo:
        await service.add_item(user_id, watchlist_id, data)
    
    assert "Watchlist not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_add_item_unauthorized(service):
    user_id = uuid4()
    other_user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")
    
    watchlist = MagicMock()
    watchlist.user_id = other_user_id

    service.watchlist_repo.get_by_id.return_value = watchlist
        
    with pytest.raises(UnauthorizedException):
        await service.add_item(user_id, watchlist_id, data)

@pytest.mark.asyncio
async def test_add_item_limit_reached(service):
    user_id = uuid4()
    watchlist_id = uuid4()
    data = MagicMock(instrument_id="INST1")
    
    watchlist = MagicMock()
    watchlist.user_id = user_id

    service.watchlist_repo.get_by_id.return_value = watchlist
    service.repo.count_items.return_value = WatchlistItemService.MAX_ITEMS
        
    with pytest.raises(BadRequestException) as excinfo:
        await service.add_item(user_id, watchlist_id, data)
    
    assert "Watchlist item limit reached" in str(excinfo.value)
