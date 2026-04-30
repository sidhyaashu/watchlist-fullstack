"""
Redis-backed API Key Repository.

API keys are stored in Redis as hashes:
  Key:   apikey:<hashed_key>
  Field: sub, scope, active

To provision a new API key (from admin tooling):
  HSET apikey:<sha256(raw_key)> sub "client_id" scope "read" active "1"
"""
import hashlib
import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def _hash_key(raw_key: str) -> str:
    """Hash the raw API key before lookup using a salt to prevent rainbow table attacks."""
    salt = settings.API_KEY_SALT or settings.SECRET_KEY
    salted_key = f"{salt}:{raw_key}"
    return hashlib.sha256(salted_key.encode()).hexdigest()


async def lookup_api_key(raw_key: str) -> dict | None:
    """
    Returns the API key payload dict if the key is valid and active,
    or None if not found / inactive.
    """
    hashed = _hash_key(raw_key)
    redis_key = f"apikey:{hashed}"

    data = await redis_client.hgetall(redis_key)

    if not data:
        return None

    if data.get("active") != "1":
        return None

    return {
        "sub": data.get("sub", "unknown"),
        "scope": data.get("scope", "read"),
    }
