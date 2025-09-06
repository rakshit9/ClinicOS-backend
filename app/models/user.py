"""User data models."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class UserInDB(BaseModel):
    """User document as stored in database."""
    
    id: Optional[str] = Field(None, alias="_id")
    email: str = Field(..., description="User email address")
    password_hash: str = Field(..., description="Hashed password")
    name: str = Field(..., description="User full name")
    role: Literal["doctor", "admin"] = Field(default="doctor", description="User role")
    verified: bool = Field(default=False, description="Email verification status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """User creation data."""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    name: str = Field(..., min_length=1, description="User full name")
    role: Literal["doctor", "admin"] = Field(default="doctor", description="User role")


class UserUpdate(BaseModel):
    """User update data."""
    
    name: Optional[str] = Field(None, min_length=1, description="User full name")
    role: Optional[Literal["doctor", "admin"]] = Field(None, description="User role")
    verified: Optional[bool] = Field(None, description="Email verification status")


class UserOut(BaseModel):
    """Public user data."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    role: Literal["doctor", "admin"] = Field(..., description="User role")
    verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
