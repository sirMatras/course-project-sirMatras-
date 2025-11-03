from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int, details: dict | None = None):
        super().__init__(status_code=status_code, detail={"code": code, "message": message, "details": details or {}})


class Unauthorized(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=HTTP_401_UNAUTHORIZED)


class Forbidden(AppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(code="FORBIDDEN", message=message, status_code=HTTP_403_FORBIDDEN)


class NotFound(AppException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(code="NOT_FOUND", message=message, status_code=HTTP_404_NOT_FOUND)


class BadRequest(AppException):
    def __init__(self, message: str = "Bad Request", details: dict | None = None):
        super().__init__(code="BAD_REQUEST", message=message, status_code=HTTP_400_BAD_REQUEST, details=details)


