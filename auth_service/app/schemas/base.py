from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class BaseAPIResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Human-readable message about the operation")
    data: Optional[T] = Field(None, description="The response data, if any")

class MessageResponse(BaseModel):
    """Generic success message."""
    status: str = Field("success")
