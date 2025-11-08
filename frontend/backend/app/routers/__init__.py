"""
API Routers

REST API endpoints and WebSocket connections.
"""

from app.routers.videos import router as videos_router
from app.routers.websocket import router as websocket_router

__all__ = [
    "videos_router",
    "websocket_router",
]
