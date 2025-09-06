"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.jwt_service import verify_access_token

# Rate limiters
limiter = Limiter(key_func=get_remote_address)

# Global rate limiter
global_limiter = limiter.shared_limit(
    "100/15 minutes",
    scope="global"
)

# Auth-specific rate limiter
auth_limiter = limiter.shared_limit(
    "10/minute",
    scope="auth"
)


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    authorization: Annotated[str | None, Header()] = None
) -> User:
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
