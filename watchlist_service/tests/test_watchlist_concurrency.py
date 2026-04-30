import asyncio
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.watchlist.service.watchlist_service import WatchlistService
from app.core.exceptions import BadRequestException


@pytest.mark.asyncio
async def test_concurrency_creates_strictly_ten_watchlists():
    """
    Simulate 20 parallel requests attempting to create a watchlist.
    The advisory lock ensures they are processed sequentially, and exactly 10 succeed.
    """
    repo = AsyncMock()
    service = WatchlistService(repo=repo)
    user_id = uuid4()

    # Shared state mock to simulate database counter
    db_state = {"count": 0}

    async def mock_count_by_user(uid):
        return db_state["count"]

    async def mock_create(uid, name):
        db_state["count"] += 1
        return MagicMock(id=uuid4(), user_id=uid, name=name)

    repo.count_by_user.side_effect = mock_count_by_user
    repo.create.side_effect = mock_create
    repo.get_by_name.return_value = None
    
    # Mocking db transaction begin
    class MockTransaction:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    repo.db.begin.return_value = MockTransaction()

    # Ensure lock acquisition simulates a slight processing delay to test concurrency
    async def mock_acquire_lock(uid):
        await asyncio.sleep(0.01)

    repo.acquire_user_lock.side_effect = mock_acquire_lock

    async def worker(index):
        try:
            return await service.create_watchlist(user_id, f"Watchlist {index}")
        except BadRequestException:
            return None

    # Run 20 concurrent requests
    results = await asyncio.gather(*(worker(i) for i in range(20)))

    # Evaluate results
    successes = [r for r in results if r is not None]
    failures = [r for r in results if r is None]

    assert len(successes) == 10, f"Expected 10 successes, got {len(successes)}"
    assert len(failures) == 10, f"Expected 10 failures, got {len(failures)}"
    assert db_state["count"] == 10, f"Database count should be 10, got {db_state['count']}"
