"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.models.user import UserInDB
from app.repositories.reset_repo import ResetRepository
from app.repositories.token_repo import TokenRepository
from app.repositories.user_repo import UserRepository
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
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize auth service."""
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.reset_repo = ResetRepository(db)
    
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
        user = await self.user_repo.create_user(request)
        
        # Generate tokens
        jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), jti)
        
        # Store refresh token
        token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_lifetime_seconds)
        await self.token_repo.save_refresh_token(
            user_id=str(user.id),
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        # Prepare response
        user_out = self.user_repo.to_public(user)
        tokens = TokensResponse(access=access_token, refresh=refresh_token)
        
        return AuthResponse(user=user_out, tokens=tokens)
    
    async def login(
        self, 
        request: LoginRequest, 
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        previous_refresh_token: Optional[str] = None
    ) -> AuthResponse:
        """Login user."""
        # Find user
        user = await self.user_repo.find_by_email(request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Revoke previous refresh token if provided (optional rotation)
        if previous_refresh_token:
            try:
                jti = get_jti_from_token(previous_refresh_token)
                if jti:
                    await self.token_repo.revoke_refresh_token(jti)
            except Exception:
                # Ignore invalid previous token
                pass
        
        # Generate new tokens
        jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), jti)
        
        # Store new refresh token
        token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_lifetime_seconds)
        await self.token_repo.save_refresh_token(
            user_id=str(user.id),
            jti=jti,
            token_hash=token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )
        
        # Prepare response
        user_out = self.user_repo.to_public(user)
        tokens = TokensResponse(access=access_token, refresh=refresh_token)
        
        return AuthResponse(user=user_out, tokens=tokens)
    
    async def refresh(self, request: LogoutRequest) -> TokensResponse:
        """Refresh access token."""
        # Verify refresh token
        try:
            payload = verify_refresh_token(request.refreshToken)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await self.user_repo.get_by_id(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Verify token in database
        token_hash = sha256_hex(request.refreshToken)
        stored_token = await self.token_repo.find_valid_by_jti_and_hash(
            payload["jti"], token_hash
        )
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Revoke old token
        await self.token_repo.revoke_refresh_token(payload["jti"])
        
        # Generate new tokens
        new_jti = generate_jti()
        access_token = sign_access_token(str(user.id), user.role)
        refresh_token = sign_refresh_token(str(user.id), new_jti)
        
        # Store new refresh token
        new_token_hash = sha256_hex(refresh_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_lifetime_seconds)
        await self.token_repo.save_refresh_token(
            user_id=str(user.id),
            jti=new_jti,
            token_hash=new_token_hash,
            user_agent=stored_token.user_agent,
            ip_address=stored_token.ip_address,
            expires_at=expires_at
        )
        
        return TokensResponse(access=access_token, refresh=refresh_token)
    
    async def logout(self, request: LogoutRequest) -> None:
        """Logout user."""
        # Get JTI from token
        jti = get_jti_from_token(request.refreshToken)
        if jti:
            await self.token_repo.revoke_refresh_token(jti)
    
    async def get_current_user(self, user_id: str) -> UserOut:
        """Get current user information."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return self.user_repo.to_public(user)
    
    async def forgot_password(self, request: ForgotPasswordRequest) -> None:
        """Send password reset email."""
        # Find user (don't reveal if email exists)
        user = await self.user_repo.find_by_email(request.email)
        if not user:
            # Return success even if user doesn't exist (security)
            return
        
        # Generate reset token
        reset_token = random_token()
        token_hash = sha256_hex(reset_token)
        expires_at = datetime.utcnow() + timedelta(seconds=settings.reset_token_lifetime_seconds)
        
        # Store reset token
        await self.reset_repo.save_reset_token(
            user_id=str(user.id),
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        # Send email
        reset_link = f"{settings.app_url}/reset?token={reset_token}"
        await email_service.send_reset_email(request.email, reset_link)
    
    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Reset user password."""
        # Find and delete valid reset token
        token_hash = sha256_hex(request.token)
        user_id = await self.reset_repo.find_and_delete_if_valid(token_hash)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        success = await self.user_repo.update_password(user_id, request.newPassword)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        # Revoke all refresh tokens for user
        await self.token_repo.revoke_all_for_user(user_id)
