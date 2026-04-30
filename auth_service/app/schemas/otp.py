from pydantic import BaseModel, EmailStr, Field, validator

class ForgotPassword(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")

class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")

class VerifyResetOTP(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    otp: str = Field(..., min_length=6, max_length=6, example="123456")

class VerifyResetOTPResponse(BaseModel):
    reset_token: str = Field(..., description="One-time token for password reset")

class ResetPassword(BaseModel):
    reset_token: str = Field(..., description="Token received after OTP verification")
    new_password: str = Field(..., min_length=8, example="NewAdmin@123")
    confirm_password: str = Field(..., example="NewAdmin@123")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v

class SetupPasswordVerifyOTP(BaseModel):
    otp: str = Field(..., min_length=6, max_length=6, example="123456")
    new_password: str = Field(..., min_length=8, example="NewAdmin@123")
    confirm_password: str = Field(..., example="NewAdmin@123")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match")
        return v
