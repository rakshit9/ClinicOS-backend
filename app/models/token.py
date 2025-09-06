"""Token data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RefreshTokenInDB(BaseModel):
    """Refresh token document as stored in database."""
    
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User ID")
    jti: str = Field(..., description="JWT ID")
    token_hash: str = Field(..., description="SHA256 hash of the token")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address")
    revoked: bool = Field(default=False, description="Token revocation status")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResetTokenInDB(BaseModel):
    """Password reset token document as stored in database."""
    
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User ID")
    token_hash: str = Field(..., description="SHA256 hash of the token")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
