"""Database connection and session management."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.models.base import Base

# Create async engine
engine = create_async_engine(
    settings.database_url,
    future=True,
    echo=False,
    # SQLite specific settings
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    } if "sqlite" in settings.database_url else {},
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database with tables and PRAGMAs."""
    logger.info("🔧 Initializing database...")
    
    # Set SQLite PRAGMAs for better performance and reliability
    async with engine.begin() as conn:
        if "sqlite" in settings.database_url:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA synchronous=NORMAL"))
            await conn.execute(text("PRAGMA cache_size=1000"))
            await conn.execute(text("PRAGMA temp_store=MEMORY"))
            logger.info("✅ SQLite PRAGMAs configured")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")
        
        # Clean up expired tokens
        await cleanup_expired_tokens(conn)
        logger.info("✅ Expired tokens cleaned up")


async def cleanup_expired_tokens(conn) -> None:
    """Clean up expired refresh and reset tokens."""
    # Clean up expired refresh tokens
    result = await conn.execute(
        text("DELETE FROM refresh_tokens WHERE expires_at < datetime('now')")
    )
    logger.info(f"🗑️ Cleaned up {result.rowcount} expired refresh tokens")
    
    # Clean up expired reset tokens
    result = await conn.execute(
        text("DELETE FROM reset_tokens WHERE expires_at < datetime('now')")
    )
    logger.info(f"🗑️ Cleaned up {result.rowcount} expired reset tokens")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with automatic commit/rollback."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connections."""
    logger.info("🛑 Closing database connections...")
    await engine.dispose()
    logger.info("✅ Database connections closed")
