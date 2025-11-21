"""
WebSocket manager for real-time video progress updates.
"""

import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for video progress updates."""

    def __init__(self):
        # video_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # connection -> video_id mapping for cleanup
        self.connection_video_map: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, video_id: str):
        """Accept a new WebSocket connection for a video."""
        await websocket.accept()

        if video_id not in self.active_connections:
            self.active_connections[video_id] = set()

        self.active_connections[video_id].add(websocket)
        self.connection_video_map[websocket] = video_id

        logger.info(
            f"WebSocket connected for video {video_id}. Active connections: {len(self.active_connections[video_id])}"
        )

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        video_id = self.connection_video_map.pop(websocket, None)

        if video_id and video_id in self.active_connections:
            self.active_connections[video_id].discard(websocket)

            # Clean up empty connections
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]

            logger.info(
                f"WebSocket disconnected for video {video_id}. Active connections: {len(self.active_connections.get(video_id, set()))}"
            )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast_to_video(self, video_id: str, message: dict):
        """Broadcast a message to all connections for a specific video."""
        if video_id not in self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected_connections = []

        for connection in self.active_connections[video_id].copy():
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)

        # Clean up disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)

    async def broadcast_progress_update(
        self,
        video_id: str,
        progress: int,
        stage: str = "",
        status: str = "",
        error: str = None,
    ):
        """Broadcast a progress update for a video."""
        message = {
            "type": "progress",
            "data": {
                "video_id": video_id,
                "progress": progress,
                "stage": stage,
                "status": status,
            },
        }

        if error:
            message["type"] = "error"
            message["data"]["error"] = error

        await self.broadcast_to_video(video_id, message)

    async def broadcast_completion(
        self, video_id: str, output_url: str = "", thumbnail_url: str = ""
    ):
        """Broadcast video completion."""
        message = {
            "type": "complete",
            "data": {
                "video_id": video_id,
                "progress": 100,
                "status": "completed",
                "output_url": output_url,
                "thumbnail_url": thumbnail_url,
            },
        }

        await self.broadcast_to_video(video_id, message)

    def get_connection_count(self, video_id: str) -> int:
        """Get the number of active connections for a video."""
        return len(self.active_connections.get(video_id, set()))

    def get_total_connections(self) -> int:
        """Get the total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())


# Global connection manager instance
connection_manager = ConnectionManager()
