"""Cryptographic utilities."""

import hashlib
import secrets
from typing import Optional

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def random_token(bytes_length: int = 32) -> str:
    """Generate a random token as hex string."""
    return secrets.token_hex(bytes_length)


def sha256_hex(data: str) -> str:
    """Generate SHA256 hash of a string as hex."""
    return hashlib.sha256(data.encode()).hexdigest()
