"""
OmniVid AI Backend Application

AI-powered video generation platform with FastAPI, Celery, PostgreSQL, and Remotion.
"""

__version__ = "1.0.0"
__author__ = "OmniVid Team"
__description__ = "Video generation API with distributed task processing"

from app.config import settings

__all__ = ["settings"]
