from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    MARKET_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://localhost:6379/0"
    SERVICE_NAME: str = "watchlist_service"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()