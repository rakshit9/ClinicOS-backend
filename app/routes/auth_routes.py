"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import auth_limiter, get_current_user, global_limiter
from app.db import get_session
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokensResponse,
)
from app.services.auth_service import AuthService
from app.utils.responses import created, no_content, ok

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@global_limiter
async def register(
    request: Request,
    register_data: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Register a new user."""
    auth_service = AuthService(session)
    result = await auth_service.register(register_data)
    return result


@router.post("/login", response_model=AuthResponse)
@auth_limiter
async def login(
    request: Request,
    login_data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None
):
    """Login user."""
    auth_service = AuthService(session)
    
    # Get client IP
    ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else None
    
    result = await auth_service.login(login_data, user_agent, ip)
    return result


@router.post("/refresh", response_model=TokensResponse)
@global_limiter
async def refresh(
    request: Request,
    refresh_data: LogoutRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Refresh access token."""
    auth_service = AuthService(session)
    result = await auth_service.refresh(refresh_data)
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@global_limiter
async def logout(
    request: Request,
    logout_data: LogoutRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Logout user."""
    auth_service = AuthService(session)
    await auth_service.logout(logout_data)
    return no_content()


@router.get("/me")
@global_limiter
async def get_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current user information."""
    return current_user.to_public()


@router.post("/forgot-password")
@auth_limiter
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Send password reset email."""
    auth_service = AuthService(session)
    result = await auth_service.forgot_password(forgot_data)
    return result


@router.post("/reset-password")
@global_limiter
async def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    """Reset user password."""
    auth_service = AuthService(session)
    result = await auth_service.reset_password(reset_data)
    return result
