"""JWT token service."""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import HTTPException, status

from app.config import settings


class JWTError(Exception):
    """Base JWT exception."""
    pass


class TokenExpiredError(JWTError):
    """Token has expired."""
    pass


class InvalidTokenError(JWTError):
    """Token is invalid."""
    pass


def generate_jti() -> str:
    """Generate a unique JWT ID."""
    return secrets.token_urlsafe(32)


def sign_access_token(user_id: str, role: str) -> str:
    """Sign an access token."""
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=settings.jwt_access_lifetime_seconds)
    }
    
    return jwt.encode(payload, settings.jwt_access_secret, algorithm="HS256")


def sign_refresh_token(user_id: str, jti: str) -> str:
    """Sign a refresh token."""
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=settings.jwt_refresh_lifetime_seconds)
    }
    
    return jwt.encode(payload, settings.jwt_refresh_secret, algorithm="HS256")


def verify_access_token(token: str) -> Dict:
    """Verify and decode an access token."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_access_secret, 
            algorithms=["HS256"]
        )
        
        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Access token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid access token")


def verify_refresh_token(token: str) -> Dict:
    """Verify and decode a refresh token."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_refresh_secret, 
            algorithms=["HS256"]
        )
        
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid refresh token")


def get_jti_from_token(token: str) -> Optional[str]:
    """Extract JTI from a refresh token without verification."""
    try:
        # Decode without verification to get JTI
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("jti")
    except jwt.InvalidTokenError:
        return None
