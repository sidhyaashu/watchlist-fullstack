"""
Redis Circuit Breaker for Watchlist Service.

Prevents cascading failure when Redis is down or slow.

States:
  CLOSED    — normal operation, all requests go through
  OPEN      — Redis is failing; requests bypass cache immediately (no wait, no retry)
  HALF_OPEN — recovery probe; one request is allowed through to test if Redis recovered

Why this matters:
  Without a circuit breaker, every request during a Redis outage will:
  1. Try to connect to Redis
  2. Wait for the socket timeout (100ms)
  3. Get an exception
  4. Fall back to DB

  With the breaker OPEN, step 1–3 are skipped entirely.
  The service stays fast under failure.
"""
import time
import threading
from enum import Enum
from app.utils.logger import logger


class _State(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class RedisCircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,   # failures in window to open the circuit
        recovery_timeout: float = 30,  # seconds before probing again
        success_threshold: int = 2,    # consecutive successes needed to close again
    ):
        self._state = _State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold
        self._lock = threading.Lock()  # thread-safe state transitions

    @property
    def state(self) -> str:
        return self._state.value

    def allow_request(self) -> bool:
        """
        Returns True if the request should attempt to use Redis.
        Returns False if the circuit is OPEN (skip Redis entirely).
        """
        with self._lock:
            if self._state == _State.CLOSED:
                return True

            if self._state == _State.OPEN:
                if time.monotonic() - self._last_failure_time >= self._recovery_timeout:
                    self._state = _State.HALF_OPEN
                    self._success_count = 0
                    logger.info("[circuit_breaker] state=HALF_OPEN probing Redis")
                    return True
                return False  # still open — bypass immediately

            # HALF_OPEN: allow through to test recovery
            return True

    def record_success(self):
        with self._lock:
            if self._state == _State.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._success_threshold:
                    self._state = _State.CLOSED
                    self._failure_count = 0
                    logger.info("[circuit_breaker] state=CLOSED Redis recovered")
            elif self._state == _State.CLOSED:
                self._failure_count = 0  # reset on success

    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == _State.HALF_OPEN:
                # Probe failed — go back to OPEN
                self._state = _State.OPEN
                logger.warning("[circuit_breaker] state=OPEN recovery probe failed")

            elif self._failure_count >= self._failure_threshold:
                self._state = _State.OPEN
                logger.error(
                    f"[circuit_breaker] state=OPEN failures={self._failure_count} "
                    f"threshold={self._failure_threshold}"
                )


# Singleton — shared across all requests in the process
redis_circuit_breaker = RedisCircuitBreaker()
