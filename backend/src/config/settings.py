import os
from typing import Optional

# Application settings
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
APP_NAME: str = "OmniVid API"
APP_VERSION: str = "0.1.0"

# Redis settings
REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

# Celery settings
CELERY_BROKER_URL: str = os.getenv(
    "CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_RESULT_BACKEND: str = os.getenv(
    "CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)

# File paths
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "/app/output")
ASSETS_DIR: str = os.getenv("ASSETS_DIR", "/app/assets")
TEMP_DIR: str = os.getenv("TEMP_DIR", "/app/tmp")

# JWT settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
