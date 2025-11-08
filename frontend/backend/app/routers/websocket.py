from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import redis.asyncio as aioredis
from app.config import settings

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        # video_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None
        self.pubsub = None
    
    async def connect(self, websocket: WebSocket, video_id: str):
        """Accept WebSocket connection and subscribe to video updates"""
        await websocket.accept()
        
        if video_id not in self.active_connections:
            self.active_connections[video_id] = set()
        
        self.active_connections[video_id].add(websocket)
        
        # Initialize Redis connection if not exists
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
        
        # Subscribe to video-specific channel
        await self.pubsub.subscribe(f"video:{video_id}")
        
        print(f"WebSocket connected for video: {video_id}")
    
    def disconnect(self, websocket: WebSocket, video_id: str):
        """Remove WebSocket connection"""
        if video_id in self.active_connections:
            self.active_connections[video_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]
        
        print(f"WebSocket disconnected for video: {video_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific websocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast_to_video(self, video_id: str, message: dict):
        """Broadcast message to all connections watching a specific video"""
        if video_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[video_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to connection: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected websockets
            for conn in disconnected:
                self.active_connections[video_id].discard(conn)
    
    async def listen_to_redis(self):
        """Listen to Redis pub/sub and broadcast to WebSocket clients"""
        if not self.pubsub:
            return
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])
                    
                    # Extract video_id from channel name (format: "video:VIDEO_ID")
                    video_id = channel.split(":")[-1]
                    
                    # Broadcast to all connected clients for this video
                    await self.broadcast_to_video(video_id, data)
        except Exception as e:
            print(f"Error in Redis listener: {e}")


manager = ConnectionManager()


@router.websocket("/ws/videos/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: str):
    """
    WebSocket endpoint for real-time video progress updates
    
    Client connects with video_id and receives real-time updates:
    - progress: 0-100
    - stage: parsing, rendering, encoding, finalizing
    - status: pending, parsing, rendering, encoding, finalizing, success, failed
    """
    await manager.connect(websocket, video_id)
    
    # Start Redis listener in background
    listener_task = asyncio.create_task(manager.listen_to_redis())
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "message": f"Connected to video {video_id}",
            "video_id": video_id
        }, websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (e.g., ping/pong)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON"
                }, websocket)
            except Exception as e:
                print(f"Error in WebSocket loop: {e}")
                break
    
    finally:
        manager.disconnect(websocket, video_id)
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": {
            video_id: len(connections)
            for video_id, connections in manager.active_connections.items()
        },
        "total_connections": sum(
            len(connections)
            for connections in manager.active_connections.values()
        )
    }
