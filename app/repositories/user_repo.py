"""User repository for database operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserCreate, UserUpdate
from app.services.crypto_service import hash_password


class UserRepository:
    """User repository for database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        self.session = session
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(
            email=user_data.email.lower().strip(),
            password_hash=hash_password(user_data.password),
            name=user_data.name.strip(),
            role=user_data.role,
            verified=False
        )
        
        try:
            self.session.add(user)
            await self.session.flush()  # Get the ID without committing
            return user
        except IntegrityError as e:
            if "uq_users_email" in str(e):
                raise ValueError("User with this email already exists")
            raise
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return user
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        await self.session.flush()
        return user
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.password_hash = hash_password(new_password)
        await self.session.flush()
        return True
    
    async def exists_email(self, email: str) -> bool:
        """Check if email exists."""
        result = await self.session.execute(
            select(User.id).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none() is not None
