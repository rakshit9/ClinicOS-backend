"""Reset token SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ResetToken(UUIDMixin, TimestampMixin, Base):
    """Reset token model."""
    
    __tablename__ = "reset_tokens"
    
    user_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reset_tokens")
    
    __table_args__ = (
        Index("ix_reset_tokens_expires_at", "expires_at"),
        UniqueConstraint("token_hash", name="uq_reset_tokens_token_hash"),
    )
