"""Refresh token repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Refresh token repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize refresh token repository."""
        self.session = session
    
    async def save_refresh(
        self,
        user_id: str,
        jti: str,
        token_hash: str,
        user_agent: Optional[str] = None,
        ip: Optional[str] = None,
        expires_at: datetime = None
    ) -> RefreshToken:
        """Save a new refresh token."""
        refresh_token = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            user_agent=user_agent,
            ip=ip,
            expires_at=expires_at,
            revoked=False
        )
        
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token
    
    async def find_valid(
        self,
        jti: str,
        token_hash: str,
        now: datetime
    ) -> Optional[RefreshToken]:
        """Find a valid refresh token by JTI and hash."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.jti == jti,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now
            )
        )
        return result.scalar_one_or_none()
    
    async def revoke(self, jti: str) -> bool:
        """Revoke a refresh token by JTI."""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        token = result.scalar_one_or_none()
        
        if token:
            token.revoked = True
            await self.session.flush()
            return True
        return False
    
    async def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.revoked = True
            count += 1
        
        if count > 0:
            await self.session.flush()
        
        return count
    
    async def cleanup_expired(self, now: datetime) -> int:
        """Clean up expired refresh tokens."""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.expires_at <= now)
        )
        expired_tokens = result.scalars().all()
        
        count = 0
        for token in expired_tokens:
            await self.session.delete(token)
            count += 1
        
        if count > 0:
            await self.session.flush()
        
        return count
