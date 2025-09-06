"""Common dependencies."""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.db import get_database
from app.services.auth_service import AuthService
from app.services.jwt_service import verify_access_token
from app.utils.responses import error


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Auth-specific rate limiter (stricter limits)
auth_limiter = Limiter(key_func=get_remote_address)


async def get_current_user(
    request: Request,
    authorization: Optional[str] = None
) -> Dict[str, str]:
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = verify_access_token(token)
        user_id = payload["sub"]
        
        # Get database and auth service
        db = await get_database()
        auth_service = AuthService(db)
        
        # Get user info
        user = await auth_service.get_current_user(user_id)
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def get_auth_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> AuthService:
    """Get authentication service."""
    return AuthService(db)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler."""
    return error(
        message="Rate limit exceeded",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        code="RATE_LIMIT_EXCEEDED",
        details={
            "retry_after": exc.retry_after,
            "limit": exc.detail
        }
    )
