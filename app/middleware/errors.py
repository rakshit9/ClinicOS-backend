"""Error handling middleware."""

from typing import Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pymongo.errors import InvalidURI
from pymongo.errors import DuplicateKeyError, PyMongoError
from pydantic import ValidationError

from app.services.jwt_service import InvalidTokenError, TokenExpiredError
from app.utils.responses import error


def setup_error_handlers(app: FastAPI):
    """Setup error handlers for the FastAPI app."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return error(
            message=exc.detail,
            status_code=exc.status_code,
            code="HTTP_ERROR"
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return error(
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            details={"errors": errors}
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors."""
        errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return error(
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            details={"errors": errors}
        )
    
    @app.exception_handler(TokenExpiredError)
    async def token_expired_exception_handler(request: Request, exc: TokenExpiredError):
        """Handle token expired errors."""
        return error(
            message="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED"
        )
    
    @app.exception_handler(InvalidTokenError)
    async def invalid_token_exception_handler(request: Request, exc: InvalidTokenError):
        """Handle invalid token errors."""
        return error(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_TOKEN"
        )
    
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
        """Handle duplicate key errors."""
        return error(
            message="Resource already exists",
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_KEY"
        )
    
    @app.exception_handler(PyMongoError)
    async def pymongo_exception_handler(request: Request, exc: PyMongoError):
        """Handle PyMongo errors."""
        logger.error(f"Database error: {exc}")
        return error(
            message="Database error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR"
        )
    
    @app.exception_handler(InvalidURI)
    async def invalid_uri_exception_handler(request: Request, exc: InvalidURI):
        """Handle invalid MongoDB URI errors."""
        logger.error(f"Invalid MongoDB URI: {exc}")
        return error(
            message="Database connection error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_CONNECTION_ERROR"
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return error(
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR"
        )
