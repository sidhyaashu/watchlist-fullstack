"""
CacheService — a single, hardened abstraction over Redis.

Responsibilities:
  - Versioned key namespace (v1:) — bump the version to nuke all old cache instantly
  - Transparent Redis failure fallback — Redis down = graceful DB fallback, never a 500
  - Cache stampede protection — NX lock prevents the thundering-herd problem on expiry
  - Hit / miss metrics — structured logs, ready for Prometheus scraping later
"""
import asyncio
import json
from typing import Any, Optional
from app.cache.redis_client import redis_client
from app.utils.logger import logger

# Bump this to instantly invalidate ALL cache across the service without flushing Redis.
# v1 → v2 means every old key is silently treated as a miss.
CACHE_VERSION = "v1"

# How long the stampede lock is held (seconds).
# Should be slightly longer than your slowest DB query.
_LOCK_TTL_SECONDS = 5

# How long to wait between stampede lock retries
_LOCK_RETRY_SLEEP = 0.05  # 50ms


class CacheService:
    """
    Stateless helper. All methods are static — import and call directly.
    Uses the global redis_client so connection pooling is shared.
    """

    @staticmethod
    def _vk(key: str) -> str:
        """Prefix every key with the cache version namespace."""
        return f"{CACHE_VERSION}:{key}"

    @staticmethod
    def _lock_key(key: str) -> str:
        return f"{CACHE_VERSION}:lock:{key}"

    # ─── Core Get / Set / Delete ───────────────────────────────────────────────

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Fetch from Redis. Returns None on miss OR on any Redis error.
        Callers must handle None as a cache miss and fall back to DB.
        """
        vk = CacheService._vk(key)
        try:
            data = await redis_client.get(vk)
            if data is not None:
                logger.debug(f"[cache:hit] key={vk}")
                return json.loads(data)
            logger.debug(f"[cache:miss] key={vk}")
            return None
        except Exception as exc:
            # Redis is down or network error — degrade gracefully
            logger.warning(f"[cache:error:get] key={vk} err={exc}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int):
        """
        Store a JSON-serialisable value. Silently skips on Redis errors
        so a write failure never surfaces as a 500 to the user.
        """
        vk = CacheService._vk(key)
        try:
            await redis_client.set(vk, json.dumps(value, default=str), ex=ttl)
        except Exception as exc:
            logger.warning(f"[cache:error:set] key={vk} err={exc}")

    @staticmethod
    async def delete(key: str):
        """Delete a single versioned key."""
        vk = CacheService._vk(key)
        try:
            await redis_client.delete(vk)
            logger.debug(f"[cache:invalidate] key={vk}")
        except Exception as exc:
            logger.warning(f"[cache:error:delete] key={vk} err={exc}")

    @staticmethod
    async def delete_pattern(pattern: str):
        """
        SCAN-based bulk invalidation — safe for production (no KEYS command).
        pattern should NOT include the version prefix; it is added automatically.
        e.g. delete_pattern("watchlists:{user_id}:*")
        """
        vp = CacheService._vk(pattern)
        try:
            async for key in redis_client.scan_iter(match=vp, count=100):
                await redis_client.delete(key)
            logger.debug(f"[cache:invalidate:pattern] pattern={vp}")
        except Exception as exc:
            logger.warning(f"[cache:error:delete_pattern] pattern={vp} err={exc}")

    # ─── Stampede Protection ───────────────────────────────────────────────────

    @staticmethod
    async def get_or_set(key: str, ttl: int, fetcher) -> Any:
        """
        Cache-aside with stampede protection.

        Flow:
          1. Try cache → return on hit
          2. Try to acquire NX lock
             a. Got lock → call fetcher(), populate cache, release lock
             b. No lock  → another worker is fetching; sleep briefly and retry from cache

        The fetcher must be an async callable that returns a JSON-serialisable value.

        Usage:
            data = await CacheService.get_or_set(
                key="watchlists:user123:0:20",
                ttl=300,
                fetcher=lambda: repo.get_by_user(user_id, 0, 20)
            )
        """
        # Fast path — cache hit (most requests)
        cached = await CacheService.get(key)
        if cached is not None:
            return cached

        lock_key = CacheService._lock_key(key)
        vk = CacheService._vk(key)
        lock_vk = CacheService._vk(lock_key)  # keep lock in same namespace

        acquired = False
        try:
            acquired = await redis_client.set(lock_vk, "1", nx=True, ex=_LOCK_TTL_SECONDS)
        except Exception as exc:
            logger.warning(f"[cache:stampede:lock_fail] key={vk} err={exc}")

        if acquired:
            try:
                # We hold the lock — fetch from DB and populate cache
                data = await fetcher()
                await CacheService.set(key, data, ttl)
                return data
            finally:
                try:
                    await redis_client.delete(lock_vk)
                except Exception:
                    pass  # lock will expire naturally
        else:
            # Another request is already fetching — wait briefly and retry from cache
            await asyncio.sleep(_LOCK_RETRY_SLEEP)
            cached = await CacheService.get(key)
            if cached is not None:
                return cached
            # Lock holder may have failed — fall through to own DB fetch
            return await fetcher()
