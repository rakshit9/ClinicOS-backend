"""Database connection and index management."""

from datetime import datetime, timedelta
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel

from app.config import settings


class Database:
    """Database connection manager."""
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


db = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    return db.database


async def connect_to_mongo():
    """Create database connection."""
    db.client = AsyncIOMotorClient(settings.mongo_uri)
    db.database = db.client.get_default_database()
    
    # Ensure indexes
    await ensure_indexes()


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()


async def ensure_indexes():
    """Create necessary database indexes."""
    # Users collection indexes
    users_collection = db.database.users
    await users_collection.create_index(
        [("email", ASCENDING)], 
        unique=True, 
        name="email_unique"
    )
    
    # Refresh tokens collection indexes
    refresh_tokens_collection = db.database.refresh_tokens
    await refresh_tokens_collection.create_index(
        [("user_id", ASCENDING), ("revoked", ASCENDING)],
        name="user_revoked"
    )
    await refresh_tokens_collection.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,  # TTL index
        name="expires_at_ttl"
    )
    
    # Reset tokens collection indexes
    reset_tokens_collection = db.database.reset_tokens
    await reset_tokens_collection.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0,  # TTL index
        name="expires_at_ttl"
    )
