"""
HTTP Cache Utilities

Provides ETag generation and Cache-Control header construction for API responses.

Why this matters:
  - ETag: client sends back If-None-Match; if data unchanged, we return 304 Not Modified
           → zero response body transfer, minimal latency
  - Cache-Control: tells NGINX, CDN, and the browser exactly how long to trust the response
           → repeated identical reads never reach the service

For authenticated endpoints, we use:
  - private → tells CDN/proxy NOT to cache (response is user-specific)
  - must-revalidate → client must check freshness after max-age expires
"""
import hashlib
import json
from typing import Any


def make_etag(data: Any) -> str:
    """
    Generate a stable, short ETag from any JSON-serialisable payload.
    Uses MD5 (not for security — purely for fast equality comparison).
    The W/ prefix marks it as a "weak" ETag (semantically equivalent, not byte-identical).
    """
    payload = json.dumps(data, default=str, sort_keys=True)
    digest = hashlib.md5(payload.encode()).hexdigest()[:16]
    return f'W/"{digest}"'


def cache_control_private(max_age: int = 60) -> str:
    """
    For authenticated user-specific data.
    - private: proxy/CDN must NOT cache this (it belongs to one user)
    - max-age: browser/client can reuse for this many seconds without re-requesting
    - must-revalidate: once max-age expires, client MUST revalidate before serving stale
    """
    return f"private, max-age={max_age}, must-revalidate"


def cache_control_no_store() -> str:
    """
    For write operations (POST, DELETE) — response must never be cached.
    """
    return "no-store"
