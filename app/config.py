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
    mongo_uri: str = Field(alias="MONGO_URI")
    
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
    
    @property
    def jwt_access_lifetime_seconds(self) -> int:
        """Convert JWT access expires string to seconds."""
        return self._parse_duration(self.jwt_access_expires)
    
    @property
    def jwt_refresh_lifetime_seconds(self) -> int:
        """Convert JWT refresh expires string to seconds."""
        return self._parse_duration(self.jwt_refresh_expires)
    
    @property
    def reset_token_lifetime_seconds(self) -> int:
        """Convert reset token expires minutes to seconds."""
        return self.reset_token_expires_min * 60
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string (e.g., '15m', '7d') to seconds."""
        if not duration:
            return 0
        
        # Match pattern: number followed by unit
        match = re.match(r"^(\d+)([smhd])$", duration.lower())
        if not match:
            raise ValueError(f"Invalid duration format: {duration}")
        
        value, unit = match.groups()
        value = int(value)
        
        multipliers = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
        }
        
        return value * multipliers[unit]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
