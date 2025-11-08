"""
Configuration Management

Centralized configuration for OMNIVID backend using environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "OMNIVID"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Remotion
    REMOTION_ROOT: Optional[str] = None
    REMOTION_COMPOSITION_ID: str = "MyComposition"
    NODE_PATH: str = "node"
    NPX_PATH: str = "npx"
    
    # Rendering Defaults
    DEFAULT_WIDTH: int = 1920
    DEFAULT_HEIGHT: int = 1080
    DEFAULT_FPS: int = 30
    DEFAULT_QUALITY: str = "high"
    DEFAULT_FORMAT: str = "mp4"
    RENDER_TIMEOUT: int = 600  # seconds
    
    # Storage
    OUTPUT_DIR: str = "./output"
    ASSETS_DIR: str = "./assets"
    TEMP_DIR: str = "./tmp"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour max per task
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Security
    API_KEY: Optional[str] = None
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def ensure_directories():
    """Create required directories if they don't exist."""
    directories = [
        settings.OUTPUT_DIR,
        settings.ASSETS_DIR,
        settings.TEMP_DIR
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def get_remotion_root() -> Path:
    """Get Remotion project root path."""
    if settings.REMOTION_ROOT:
        return Path(settings.REMOTION_ROOT)
    
    # Default to current directory or project root
    return Path.cwd()


def get_output_path(filename: str) -> str:
    """Get full output file path."""
    return str(Path(settings.OUTPUT_DIR) / filename)
