"""Application configuration using Pydantic Settings."""

import re
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    app_name: str = Field(default="clinic-auth-api", alias="APP_NAME")
    app_url: str = Field(default="http://localhost:8000", alias="APP_URL")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(alias="DATABASE_URL")
    
    # JWT settings
    jwt_access_secret: str = Field(alias="JWT_ACCESS_SECRET")
    jwt_refresh_secret: str = Field(alias="JWT_REFRESH_SECRET")
    jwt_access_expires: str = Field(default="15m", alias="JWT_ACCESS_EXPIRES")
    jwt_refresh_expires: str = Field(default="7d", alias="JWT_REFRESH_EXPIRES")
    
    # Password reset
    reset_token_expires_min: int = Field(default=30, alias="RESET_TOKEN_EXPIRES_MIN")
    
    # CORS
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")
    
    # Email settings
    mail_from: str = Field(alias="MAIL_FROM")
    mail_server: str = Field(alias="MAIL_SERVER")
    mail_port: int = Field(alias="MAIL_PORT")
    mail_username: str = Field(default="", alias="MAIL_USERNAME")
    mail_password: str = Field(default="", alias="MAIL_PASSWORD")
    mail_tls: bool = Field(default=True, alias="MAIL_TLS")
    
    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("jwt_access_expires", mode="after")
    @classmethod
    def parse_jwt_access_expires(cls, v):
        """Parse JWT access token expiration."""
        return cls._parse_duration(v)
    
    @field_validator("jwt_refresh_expires", mode="after")
    @classmethod
    def parse_jwt_refresh_expires(cls, v):
        """Parse JWT refresh token expiration."""
        return cls._parse_duration(v)
    
    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse duration string to seconds."""
        if not duration_str:
            return 900  # 15 minutes default
        
        # Match patterns like "15m", "7d", "1h", "30s"
        match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")
        
        value, unit = match.groups()
        value = int(value)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return value * multipliers[unit]
    
    @property
    def jwt_access_expires_seconds(self) -> int:
        """Get JWT access token expiration in seconds."""
        return self.jwt_access_expires
    
    @property
    def jwt_refresh_expires_seconds(self) -> int:
        """Get JWT refresh token expiration in seconds."""
        return self.jwt_refresh_expires
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
