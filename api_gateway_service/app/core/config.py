from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "API Gateway"

    SECRET_KEY: str
    API_KEY_SALT: str | None = None
    ALGORITHM: str = "HS256"

    # Downstream service URLs
    AUTH_SERVICE_URL: str = "http://auth_service:8000"
    NEWS_SERVICE_URL: str = "http://news_service:8001"
    MARKET_SERVICE_URL: str = "http://market_service:8002"

    # Client origin for CORS
    CLIENT_URL: str = "http://localhost:3000"

    REDIS_URL: str = "redis://redis:6379"

    # Rate limits
    RATE_LIMIT_IP: int = 100
    RATE_LIMIT_USER: int = 200
    RATE_LIMIT_AI: int = 20

    class Config:
        env_file = ".env"


settings = Settings()