"""Reset token repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reset_token import ResetToken


class ResetTokenRepository:
    """Reset token repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize reset token repository."""
        self.session = session
    
    async def save(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime
    ) -> ResetToken:
        """Save a new reset token."""
        reset_token = ResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        self.session.add(reset_token)
        await self.session.flush()
        return reset_token
    
    async def consume_if_valid(
        self,
        token_hash: str,
        now: datetime
    ) -> Optional[ResetToken]:
        """Consume a reset token if valid (atomic operation)."""
        # Find the token
        result = await self.session.execute(
            select(ResetToken).where(
                ResetToken.token_hash == token_hash,
                ResetToken.expires_at > now
            )
        )
        token = result.scalar_one_or_none()
        
        if token:
            # Delete the token (consume it)
            await self.session.delete(token)
            await self.session.flush()
            return token
        
        return None
    
    async def cleanup_expired(self, now: datetime) -> int:
        """Clean up expired reset tokens."""
        result = await self.session.execute(
            select(ResetToken).where(ResetToken.expires_at <= now)
        )
        expired_tokens = result.scalars().all()
        
        count = 0
        for token in expired_tokens:
            await self.session.delete(token)
            count += 1
        
        if count > 0:
            await self.session.flush()
        
        return count
