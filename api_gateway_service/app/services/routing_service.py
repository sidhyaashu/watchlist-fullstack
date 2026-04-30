from app.core.config import settings

ROUTES = {
    "/api/v1/auth": settings.AUTH_SERVICE_URL,
    "/api/v1/user": settings.AUTH_SERVICE_URL,
    "/api/v1/news": settings.NEWS_SERVICE_URL,
    "/api/v1/market": settings.MARKET_SERVICE_URL,
    "/api/v1/watchlists": settings.WATCHLIST_SERVICE_URL,
}


def resolve_service(path: str):
    matched_service = None
    longest_match = ""

    for prefix, service in ROUTES.items():
        if path.startswith(prefix) and len(prefix) > len(longest_match):
            longest_match = prefix
            matched_service = service

    return matched_service, longest_match