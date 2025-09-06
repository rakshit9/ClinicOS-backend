"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.repositories.refresh_repo import RefreshTokenRepository
from app.repositories.reset_repo import ResetTokenRepository
from app.repositories.user_repo import UserRepository
from app.models.user import UserCreate
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokensResponse,
)
from app.schemas.user import UserOut
from app.services.crypto_service import random_token, sha256_hex, verify_password
from app.services.email_service import email_service
from app.services.jwt_service import (
    generate_jti,
    get_jti_from_token,
    sign_access_token,
    sign_refresh_token,
    verify_refresh_token,
)


class AuthService:
    """Authentication service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize auth service."""
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_repo = RefreshTokenRepository(session)
        self.reset_repo = ResetTokenRepository(session)
    
    async def register(self, request: RegisterRequest) -> AuthResponse:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_repo.find_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Create user
        user_data = UserCreate(
            email=request.email,
            password=request.password,
            name=request.name,
            role=request.role
        )
        user = await self.user_repo.create_user(user_data)
        
        # Generate tokens
        jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), jti)
        
        # Store refresh token
        token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_expires_seconds)
        
        await self.refresh_repo.save_refresh(
            user_id=str(user.id),
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        return AuthResponse(
            user=user.to_public(),
            tokens=TokensResponse(
                access=access_token,
                refresh=refresh_token
            )
        )
    
    async def login(
        self, 
        request: LoginRequest, 
        user_agent: Optional[str] = None,
        ip: Optional[str] = None
    ) -> AuthResponse:
        """Login user."""
        # Find user
        user = await self.user_repo.find_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate tokens
        jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), jti)
        
        # Store refresh token
        token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_expires_seconds)
        
        await self.refresh_repo.save_refresh(
            user_id=str(user.id),
            jti=jti,
            token_hash=token_hash,
            user_agent=user_agent,
            ip=ip,
            expires_at=expires_at
        )
        
        return AuthResponse(
            user=user.to_public(),
            tokens=TokensResponse(
                access=access_token,
                refresh=refresh_token
            )
        )
    
    async def refresh(self, request: LogoutRequest) -> TokensResponse:
        """Refresh access token."""
        # Verify refresh token
        try:
            payload = verify_refresh_token(request.refreshToken)
            user_id = payload["sub"]
            jti = payload["jti"]
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Find user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Verify token in database
        token_hash = sha256_hex(request.refreshToken)
        stored_token = await self.refresh_repo.find_valid(
            jti=jti,
            token_hash=token_hash,
            now=datetime.utcnow()
        )
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Revoke old token
        await self.refresh_repo.revoke(jti)
        
        # Generate new tokens
        new_jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), new_jti)
        
        # Store new refresh token
        new_token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_expires_seconds)
        
        await self.refresh_repo.save_refresh(
            user_id=str(user.id),
            jti=new_jti,
            token_hash=new_token_hash,
            user_agent=stored_token.user_agent,
            ip=stored_token.ip,
            expires_at=expires_at
        )
        
        return TokensResponse(
            access=access_token,
            refresh=refresh_token
        )
    
    async def logout(self, request: LogoutRequest) -> None:
        """Logout user."""
        try:
            payload = verify_refresh_token(request.refreshToken)
            jti = payload["jti"]
        except Exception:
            # If token is invalid, consider it already logged out
            return
        
        # Revoke token
        await self.refresh_repo.revoke(jti)
    
    async def get_current_user(self, user_id: str) -> UserOut:
        """Get current user information."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user.to_public()
    
    async def forgot_password(self, request: ForgotPasswordRequest) -> dict:
        """Send password reset email."""
        user = await self.user_repo.find_by_email(request.email)
        if not user:
            # Don't reveal if email exists
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        reset_token = random_token(32)
        token_hash = sha256_hex(reset_token)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.reset_token_expires_min)
        
        # Store reset token
        await self.reset_repo.save(
            user_id=str(user.id),
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        # Send email
        reset_link = f"{settings.app_url}/reset?token={reset_token}"
        await email_service.send_reset_email(user.email, reset_link)
        
        return {"message": "If the email exists, a reset link has been sent"}
    
    async def reset_password(self, request: ResetPasswordRequest) -> dict:
        """Reset user password."""
        # Hash the provided token
        token_hash = sha256_hex(request.token)
        
        # Consume the token if valid
        reset_token = await self.reset_repo.consume_if_valid(
            token_hash=token_hash,
            now=datetime.utcnow()
        )
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        success = await self.user_repo.update_password(
            user_id=reset_token.user_id,
            new_password=request.newPassword
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        # Revoke all refresh tokens for this user
        await self.refresh_repo.revoke_all_for_user(reset_token.user_id)
        
        return {"message": "Password updated successfully"}
