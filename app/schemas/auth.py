"""Authentication request/response schemas."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.user import UserOut


class RegisterRequest(BaseModel):
    """User registration request."""
    
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    role: Literal["doctor", "admin"] = Field(default="doctor", description="User role")


class LoginRequest(BaseModel):
    """User login request."""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshRequest(BaseModel):
    """Token refresh request."""
    
    refreshToken: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """User logout request."""
    
    refreshToken: str = Field(..., description="Refresh token to revoke")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    
    email: str = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Reset password request."""
    
    token: str = Field(..., description="Password reset token")
    newPassword: str = Field(..., min_length=8, description="New password")


class TokensResponse(BaseModel):
    """Token response."""
    
    access: str = Field(..., description="Access token")
    refresh: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response."""
    
    user: UserOut = Field(..., description="User information")
    tokens: TokensResponse = Field(..., description="Authentication tokens")


class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str = Field(..., description="Response message")
