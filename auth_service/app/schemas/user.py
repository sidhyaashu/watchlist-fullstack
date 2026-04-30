import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Full name of the user", example="John Doe")
    email: EmailStr = Field(..., description="Valid email address", example="john.doe@example.com")
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number with country code", example="+1234567890")
    password: str = Field(..., min_length=8, description="Strong password", example="Admin@123")
    dob: Optional[datetime] = Field(None, description="Date of birth")

    @validator("password")
    def password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")
        return v

class ProfileResponse(BaseModel):
    user_id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="john.doe@example.com")
    name: str = Field(...)
    phone: Optional[str] = Field(None)

class ChangePassword(BaseModel):
    current_password: str = Field(..., example="Admin@123")
    new_password: str = Field(..., min_length=8, example="NewAdmin@123")
    confirm_password: str = Field(..., example="NewAdmin@123")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v
