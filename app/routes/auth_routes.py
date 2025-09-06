"""Authentication routes."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.deps import auth_limiter, get_auth_service, get_current_user
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.utils.responses import created, no_content, ok

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user."""
    result = await auth_service.register(request)
    return created(data=result.model_dump())


@router.post("/login", response_model=AuthResponse)
@auth_limiter.limit("10/minute")
async def login(
    request: LoginRequest,
    req: Request,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user."""
    # Get client IP
    ip_address = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else get_remote_address(req)
    
    result = await auth_service.login(
        request=request,
        user_agent=user_agent,
        ip_address=ip_address
    )
    return ok(data=result.model_dump())


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token."""
    result = await auth_service.refresh(request)
    return ok(data=result.model_dump())


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user."""
    await auth_service.logout(request)
    return no_content()


@router.get("/me", response_model=UserOut)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information."""
    return ok(data=current_user)


@router.post("/forgot-password", response_model=MessageResponse)
@auth_limiter.limit("10/minute")
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Send password reset email."""
    await auth_service.forgot_password(request)
    return ok(data={"message": "If the email exists, a reset link has been sent"})


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset user password."""
    await auth_service.reset_password(request)
    return ok(data={"message": "Password has been reset successfully"})
