from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="Admin@123")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid refresh token")
