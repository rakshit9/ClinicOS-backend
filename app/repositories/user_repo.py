"""User repository for database operations."""

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models.user import UserCreate, UserInDB, UserOut, UserUpdate
from app.services.crypto_service import hash_password


class UserRepository:
    """User repository for database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize user repository."""
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user."""
        user_doc = UserInDB(
            email=user_data.email.lower().strip(),
            password_hash=hash_password(user_data.password),
            name=user_data.name.strip(),
            role=user_data.role,
            verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        try:
            result = await self.collection.insert_one(user_doc.model_dump(by_alias=True, exclude={"id"}))
            user_doc.id = str(result.inserted_id)
            return user_doc
        except DuplicateKeyError:
            raise ValueError("User with this email already exists")
    
    async def find_by_email(self, email: str) -> Optional[UserInDB]:
        """Find user by email."""
        doc = await self.collection.find_one({"email": email.lower().strip()})
        if doc:
            doc["_id"] = str(doc["_id"])
            return UserInDB(**doc)
        return None
    
    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        from bson import ObjectId
        try:
            doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return UserInDB(**doc)
            return None
        except Exception:
            return None
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[UserInDB]:
        """Update user information."""
        from bson import ObjectId
        
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_by_id(user_id)
        
        update_dict["updated_at"] = datetime.utcnow()
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count:
                return await self.get_by_id(user_id)
            return None
        except Exception:
            return None
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password."""
        from bson import ObjectId
        
        password_hash = hash_password(new_password)
        
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def to_public(self, user: UserInDB) -> UserOut:
        """Convert user to public format."""
        return UserOut(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            verified=user.verified,
            created_at=user.created_at
        )
