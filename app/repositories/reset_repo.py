"""Password reset token repository for database operations."""

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.token import ResetTokenInDB


class ResetRepository:
    """Password reset token repository for database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize reset repository."""
        self.db = db
        self.collection = db.reset_tokens
    
    async def save_reset_token(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime
    ) -> ResetTokenInDB:
        """Save a password reset token."""
        reset_doc = ResetTokenInDB(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        result = await self.collection.insert_one(
            reset_doc.model_dump(by_alias=True, exclude={"id"})
        )
        reset_doc.id = str(result.inserted_id)
        return reset_doc
    
    async def find_and_delete_if_valid(self, token_hash: str) -> Optional[str]:
        """Find and atomically delete a valid reset token, returning user_id."""
        # Use findOneAndDelete for atomic operation
        doc = await self.collection.find_one_and_delete({
            "token_hash": token_hash,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if doc:
            return doc.get("user_id")
        return None
