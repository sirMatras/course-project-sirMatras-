from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import HTTPException
import uuid
import logging


logger = logging.getLogger(__name__)


def _problem_json(
    *,
    request: Request,
    status: int,
    title: str,
    detail: str | None = None,
    type_: str | None = None,
    extra: dict | None = None,
) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    payload = {
        "type": type_ or "about:blank",
        "title": title,
        "status": status,
        "detail": detail or "",
        "correlation_id": correlation_id,
    }
    if extra:
        payload.update(extra)
    return JSONResponse(status_code=status, content=payload, media_type="application/problem+json")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        # Propagate correlation ID to response headers for tracing
        response.headers["X-Correlation-ID"] = correlation_id
        return response


def add_error_handlers(app: FastAPI) -> None:
    # Install correlation-id middleware
    app.add_middleware(CorrelationIdMiddleware)

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return _problem_json(
            request=request,
            status=HTTP_422_UNPROCESSABLE_ENTITY,
            title="Input validation error",
            type_="https://example.com/problems/validation-error",
            extra={"errors": exc.errors()},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        return _problem_json(
            request=request,
            status=HTTP_422_UNPROCESSABLE_ENTITY,
            title="Input validation error",
            type_="https://example.com/problems/validation-error",
            extra={"errors": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Map common statuses to titles; mask unknowns
        status = exc.status_code or HTTP_400_BAD_REQUEST
        title_by_status = {
            HTTP_400_BAD_REQUEST: "Bad Request",
            HTTP_401_UNAUTHORIZED: "Unauthorized",
            HTTP_403_FORBIDDEN: "Forbidden",
            HTTP_404_NOT_FOUND: "Not Found",
            HTTP_429_TOO_MANY_REQUESTS: "Too Many Requests",
        }
        title = title_by_status.get(status, "Error")
        # Avoid leaking internal structures; allow simple strings
        detail = None
        if isinstance(exc.detail, str):
            detail = exc.detail
        elif isinstance(exc.detail, dict):
            detail = exc.detail.get("message") or exc.detail.get("detail") or None
        return _problem_json(
            request=request,
            status=status,
            title=title,
            type_=f"https://example.com/problems/{title.lower().replace(' ', '-')}",
            detail=detail,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Mask internal details, log with correlation id
        correlation_id = getattr(request.state, "correlation_id", "-")
        logger.exception("Unhandled error, correlation_id=%s", correlation_id)
        return _problem_json(
            request=request,
            status=HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            type_="https://example.com/problems/internal-server-error",
            detail="An unexpected error occurred. Please contact support.",
        )

