"""
WebSocket routes for real-time video progress updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from src.api.services.websocket_manager import connection_manager

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/videos/{video_id}")
async def video_progress_websocket(websocket: WebSocket, video_id: str):
    """
    WebSocket endpoint for real-time video progress updates.
    
    Args:
        websocket: WebSocket connection
        video_id: Video ID to track progress for
    """
    try:
        # In a real implementation, you would verify authentication here
        # For now, we'll allow all connections but log it
        user_id = "anonymous"  # Placeholder for authenticated user
        
        # In a real implementation, you would verify that the user has access to this video
        # For now, we'll allow all connections but log it
        logger.info(f"WebSocket connection attempt for video {video_id} by user {user_id}")
        
        # Accept the connection
        await connection_manager.connect(websocket, video_id)
        
        # Send initial connection confirmation
        await connection_manager.send_personal_message(
            websocket,
            '{"type": "connection", "data": {"status": "connected", "video_id": "' + video_id + '"}}'
        )
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                # Echo back for connection testing
                response = {
                    "type": "ping",
                    "data": {"message": "pong", "timestamp": "2025-11-16T19:07:12.250Z"}
                }
                await connection_manager.send_personal_message(websocket, str(response))
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for video {video_id}")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
    finally:
        # Clean up connection
        connection_manager.disconnect(websocket)

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status."""
    return {
        "status": "active",
        "total_connections": connection_manager.get_total_connections(),
        "active_videos": list(connection_manager.active_connections.keys())
    }

@router.post("/ws/test/broadcast")
async def test_websocket_broadcast(video_id: str, progress: int = 50, stage: str = "Testing"):
    """Test endpoint to broadcast progress updates (development only)."""
    await connection_manager.broadcast_progress_update(
        video_id=video_id,
        progress=progress,
        stage=stage,
        status="testing"
    )
    return {"message": "Test broadcast sent", "video_id": video_id, "progress": progress}