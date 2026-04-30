from typing import Any, Dict, Optional


class BaseAppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.headers = headers


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message, status_code=404)


class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message, status_code=400)


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)
