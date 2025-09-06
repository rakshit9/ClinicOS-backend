"""Error handling middleware."""

from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from app.services.jwt_service import InvalidTokenError, TokenExpiredError
from app.utils.responses import error


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return error(
        message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        details={"errors": errors}
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    error_msg = str(exc.orig)
    
    if "uq_users_email" in error_msg or "UNIQUE constraint failed" in error_msg:
        return error(
            message="User with this email already exists",
            status_code=status.HTTP_409_CONFLICT,
            code="EMAIL_EXISTS"
        )
    
    logger.error(f"Integrity error: {error_msg}")
    return error(
        message="Database constraint violation",
        status_code=status.HTTP_400_BAD_REQUEST,
        code="INTEGRITY_ERROR"
    )


async def jwt_error_handler(request: Request, exc: Union[TokenExpiredError, InvalidTokenError]) -> JSONResponse:
    """Handle JWT errors."""
    if isinstance(exc, TokenExpiredError):
        return error(
            message="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED"
        )
    else:
        return error(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN"
        )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    return error(
        message="Rate limit exceeded",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        code="RATE_LIMIT_EXCEEDED",
        details={
            "retry_after": exc.retry_after,
            "limit": exc.detail
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return error(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR"
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Setup error handlers for the FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(TokenExpiredError, jwt_error_handler)
    app.add_exception_handler(InvalidTokenError, jwt_error_handler)
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(Exception, general_exception_handler)
