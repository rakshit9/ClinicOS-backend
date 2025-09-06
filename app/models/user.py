"""User SQLAlchemy model and Pydantic schemas."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(UUIDMixin, TimestampMixin, Base):
    """User model."""
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="doctor"
    )
    verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    
    __table_args__ = (
        CheckConstraint("role IN ('doctor', 'admin')", name="check_role"),
        UniqueConstraint("email", name="uq_users_email"),
    )
    
    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reset_tokens: Mapped[list["ResetToken"]] = relationship(
        "ResetToken", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def to_public(self) -> "UserOut":
        """Convert to public user representation."""
        return UserOut(
            id=self.id,
            email=self.email,
            name=self.name,
            role=self.role,
            verified=self.verified,
            created_at=self.created_at
        )


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
