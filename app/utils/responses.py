"""Standardized API response utilities."""

from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse


def create_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    error: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized JSON response."""
    response_data = {
        "data": data,
        "message": message,
        "error": error
    }
    return JSONResponse(content=response_data, status_code=status_code)


def ok(data: Any = None, message: str = "Success") -> JSONResponse:
    """Create a successful response."""
    return create_response(data=data, message=message, status_code=status.HTTP_200_OK)


def created(data: Any = None, message: str = "Created successfully") -> JSONResponse:
    """Create a created response."""
    return create_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def no_content() -> JSONResponse:
    """Create a no content response."""
    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)


def error(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create an error response."""
    error_data = {
        "code": code,
        "message": message,
        "details": details
    }
    return create_response(
        data=None,
        message="Error",
        status_code=status_code,
        error=error_data
    )
