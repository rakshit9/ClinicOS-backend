"""Standardized response utilities."""

from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "Success") -> JSONResponse:
    """Return 200 OK response."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"data": data, "error": None, "message": message}
    )


def created(data: Any = None, message: str = "Created") -> JSONResponse:
    """Return 201 Created response."""
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"data": data, "error": None, "message": message}
    )


def no_content() -> JSONResponse:
    """Return 204 No Content response."""
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None
    )


def error(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Return error response."""
    error_data = {
        "code": code or "ERROR",
        "message": message
    }
    
    if details:
        error_data["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content={"data": None, "error": error_data}
    )
