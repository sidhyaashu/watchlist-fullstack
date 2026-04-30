from typing import Optional, List, Dict, Any, Union
from pydantic import Field, validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Auth Service"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = Field(..., description="High-entropy secret key for JWT signing")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_SECRET: str = Field(..., description="Secret key for session middleware")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL async connection URL")
    REDIS_URL: str = Field(..., description="Redis connection URL")

    # SMTP Settings (Transactional Emails)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    EMAIL_ADDRESS: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_FROM_NAME: str = "Auth Service Admin"

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Frontend Integration
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_HOSTS: Union[List[str], str] = ["http://localhost:3000"]

    # Security Policies
    ACCOUNT_LOCKOUT_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    OTP_EXPIRY_MINUTES: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]], values: Dict[str, Any]) -> List[str]:
        import json
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    res = json.loads(v_stripped)
                except json.JSONDecodeError:
                    # Fallback if it was just a string that happened to have brackets
                    res = [i.strip() for i in v_stripped.split(",")]
            else:
                res = [i.strip() for i in v_stripped.split(",")]
        elif isinstance(v, list):
            res = v
        else:
            res = [str(v)]
        
        # Flatten and clean
        res = [str(origin).rstrip("/") for origin in res if origin]
        
        # Simple security check if ENVIRONMENT is available
        env = values.get("ENVIRONMENT", "development")
        if "*" in res and env == "production":
            raise ValueError("Wildcard ALLOWED_HOSTS is not permitted in production environment.")
        return res

    @validator("DATABASE_URL", pre=True)
    def fix_postgres_scheme(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if "asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

settings = Settings()
