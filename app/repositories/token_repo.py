"""Refresh token repository for database operations."""

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.token import RefreshTokenInDB


class TokenRepository:
    """Refresh token repository for database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize token repository."""
        self.db = db
        self.collection = db.refresh_tokens
    
    async def save_refresh_token(
        self,
        user_id: str,
        jti: str,
        token_hash: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        expires_at: datetime = None
    ) -> RefreshTokenInDB:
        """Save a refresh token."""
        token_doc = RefreshTokenInDB(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            revoked=False,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        result = await self.collection.insert_one(
            token_doc.model_dump(by_alias=True, exclude={"id"})
        )
        token_doc.id = str(result.inserted_id)
        return token_doc
    
    async def find_valid_by_jti_and_hash(
        self, 
        jti: str, 
        token_hash: str
    ) -> Optional[RefreshTokenInDB]:
        """Find a valid refresh token by JTI and hash."""
        doc = await self.collection.find_one({
            "jti": jti,
            "token_hash": token_hash,
            "revoked": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if doc:
            doc["_id"] = str(doc["_id"])
            return RefreshTokenInDB(**doc)
        return None
    
    async def revoke_refresh_token(self, jti: str) -> bool:
        """Revoke a refresh token by JTI."""
        result = await self.collection.update_one(
            {"jti": jti},
            {
                "$set": {
                    "revoked": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self.collection.update_many(
            {"user_id": user_id, "revoked": False},
            {
                "$set": {
                    "revoked": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count
