import redis.asyncio as aioredis
from app.core.config import settings

# socket_connect_timeout: fail fast if Redis isn't reachable (don't block the request)
# socket_timeout: max time to wait for a Redis command to complete
# Both values are deliberately short — Redis should respond in <10ms under normal conditions.
# If it doesn't, the circuit breaker will open and bypass Redis entirely.
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8",
    socket_connect_timeout=0.5,   # 500ms to establish connection
    socket_timeout=0.2,            # 200ms per command — fail fast
)
