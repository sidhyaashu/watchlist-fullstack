"""
CacheService — hardened Redis abstraction.

Guarantees:
  - Versioned keys (v1:) — bump CACHE_VERSION to nuke all cache without flushing Redis
  - Redis failure fallback — every operation degrades gracefully to None
  - Circuit breaker — after 5 failures, Redis is bypassed for 30s (no timeout penalty per request)
  - Stampede protection — NX lock prevents thundering herd on cache expiry
  - Structured logging — hit/miss/error/circuit-state all emit JSON log lines
"""
import asyncio
import json
from typing import Any, Optional

from app.cache.redis_client import redis_client
from app.core.circuit_breaker import redis_circuit_breaker
from app.utils.logger import logger

# Bump this string to instantly invalidate ALL cache without a Redis FLUSHDB.
# Any request that finds a v1: key after bumping to v2: treats it as a miss.
CACHE_VERSION = "v1"

_LOCK_TTL_SECONDS = 5   # max time a stampede lock is held
_LOCK_RETRY_SLEEP = 0.05  # 50ms between retries when lock is contended


class CacheService:

    @staticmethod
    def _vk(key: str) -> str:
        return f"{CACHE_VERSION}:{key}"

    @staticmethod
    def _lock_key(key: str) -> str:
        return f"{CACHE_VERSION}:lock:{key}"

    # ─── Core Get / Set / Delete ───────────────────────────────────────────────

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Returns None on miss OR on any Redis/circuit-breaker bypass."""
        if not redis_circuit_breaker.allow_request():
            logger.debug(f"[cache:circuit_open] key={CacheService._vk(key)}")
            return None

        vk = CacheService._vk(key)
        try:
            data = await redis_client.get(vk)
            redis_circuit_breaker.record_success()
            if data is not None:
                logger.debug(f"[cache:hit] key={vk}")
                return json.loads(data)
            logger.debug(f"[cache:miss] key={vk}")
            return None
        except Exception as exc:
            redis_circuit_breaker.record_failure()
            logger.warning(f"[cache:error:get] key={vk} err={exc}")
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: int):
        """Silently skips on Redis errors or open circuit."""
        if not redis_circuit_breaker.allow_request():
            return

        vk = CacheService._vk(key)
        try:
            await redis_client.set(vk, json.dumps(value, default=str), ex=ttl)
            redis_circuit_breaker.record_success()
        except Exception as exc:
            redis_circuit_breaker.record_failure()
            logger.warning(f"[cache:error:set] key={vk} err={exc}")

    @staticmethod
    async def delete(key: str):
        if not redis_circuit_breaker.allow_request():
            return

        vk = CacheService._vk(key)
        try:
            await redis_client.delete(vk)
            redis_circuit_breaker.record_success()
            logger.debug(f"[cache:invalidate] key={vk}")
        except Exception as exc:
            redis_circuit_breaker.record_failure()
            logger.warning(f"[cache:error:delete] key={vk} err={exc}")

    @staticmethod
    async def delete_pattern(pattern: str):
        """SCAN-based bulk invalidation — safe for production."""
        if not redis_circuit_breaker.allow_request():
            return

        vp = CacheService._vk(pattern)
        try:
            async for key in redis_client.scan_iter(match=vp, count=100):
                await redis_client.delete(key)
            redis_circuit_breaker.record_success()
            logger.debug(f"[cache:invalidate:pattern] pattern={vp}")
        except Exception as exc:
            redis_circuit_breaker.record_failure()
            logger.warning(f"[cache:error:delete_pattern] pattern={vp} err={exc}")

    # ─── Stampede-Protected Read ───────────────────────────────────────────────

    @staticmethod
    async def get_or_set(key: str, ttl: int, fetcher) -> Any:
        """
        Cache-aside with stampede protection.
        When the circuit is OPEN, fetcher is called directly — no lock overhead.
        """
        # Fast path
        cached = await CacheService.get(key)
        if cached is not None:
            return cached

        # Circuit open — go straight to DB, no lock attempt
        if not redis_circuit_breaker.allow_request():
            return await fetcher()

        lock_key = CacheService._lock_key(key)
        acquired = False
        try:
            acquired = await redis_client.set(
                CacheService._vk(lock_key), "1", nx=True, ex=_LOCK_TTL_SECONDS
            )
        except Exception as exc:
            logger.warning(f"[cache:stampede:lock_fail] key={CacheService._vk(key)} err={exc}")

        if acquired:
            try:
                data = await fetcher()
                await CacheService.set(key, data, ttl)
                return data
            finally:
                try:
                    await redis_client.delete(CacheService._vk(lock_key))
                except Exception:
                    pass
        else:
            await asyncio.sleep(_LOCK_RETRY_SLEEP)
            cached = await CacheService.get(key)
            if cached is not None:
                return cached
            return await fetcher()
