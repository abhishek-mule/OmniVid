"""
Configuration module for OmniVid backend.

This module handles the application configuration, loading settings from environment variables
and providing default values where necessary.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "OmniVid Backend")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Video processing settings
    VIDEO_UPLOAD_DIR: str = os.getenv("VIDEO_UPLOAD_DIR", "uploads/videos")
    THUMBNAIL_UPLOAD_DIR: str = os.getenv("THUMBNAIL_UPLOAD_DIR", "uploads/thumbnails")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to a dictionary."""
        return {
            "APP_NAME": self.APP_NAME,
            "DEBUG": self.DEBUG,
            "ENVIRONMENT": self.ENVIRONMENT,
            "DATABASE_URL": self.DATABASE_URL,
            "TEST_DATABASE_URL": self.TEST_DATABASE_URL,
            "REDIS_HOST": self.REDIS_HOST,
            "REDIS_PORT": self.REDIS_PORT,
            "CORS_ORIGINS": self.CORS_ORIGINS,
        }

# Create a single instance of settings
settings = Settings()

# Create necessary directories
os.makedirs(settings.VIDEO_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.THUMBNAIL_UPLOAD_DIR, exist_ok=True)

__all__ = ["settings"]
