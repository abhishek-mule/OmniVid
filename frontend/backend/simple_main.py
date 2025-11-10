"""
OMNIVID Backend API - Simplified Version
FastAPI application for video generation (without Celery dependency)
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from pathlib import Path
import asyncio
import json
from datetime import datetime
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="OmniVid API",
    description="AI-Powered Video Generation Platform",
    version="0.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class VideoSettings(BaseModel):
    resolution: str = Field("1080p", description="Video resolution")
    fps: int = Field(30, description="Frames per second")
    duration: int = Field(15, description="Duration in seconds")
    quality: str = Field("balanced", description="Quality preset")
    template: Optional[str] = Field(None, description="Template ID")

class VideoCreateRequest(BaseModel):
    prompt: str = Field(..., description="Natural language video description")
    settings: VideoSettings = Field(default_factory=VideoSettings)

class VideoResponse(BaseModel):
    id: str
    video_id: str
    status: str
    message: str
    prompt: Optional[str] = None
    progress: int = 0
    current_stage: Optional[str] = None

class VideoStatus(BaseModel):
    video_id: str
    status: str
    progress: int
    stage: str
    output_url: Optional[str] = None
    error: Optional[str] = None

# In-memory storage (replace with database in production)
videos_db = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.ping_interval = 30  # seconds

    async def connect(self, video_id: str, websocket: WebSocket):
        origin = websocket.headers.get('origin', '')
        allowed_origins = [
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "http://localhost:3002",
            "http://localhost",
            "http://127.0.0.1"
        ]
        
        print(f"Incoming WebSocket connection for video {video_id} from origin: {origin}")
        
        try:
            # Accept the connection first to establish the WebSocket
            await websocket.accept()
            print(f"WebSocket connection accepted from {websocket.client.host if websocket.client else 'unknown'}")
            
            # Store the connection
            self.active_connections[video_id] = websocket
            print(f"Active connections for {video_id}: {len([k for k, v in self.active_connections.items() if v == websocket])}")
            
            # Send initial connection confirmation
            try:
                await websocket.send_json({
                    "type": "connection",
                    "message": f"Connected to video {video_id}",
                    "video_id": video_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                print(f"Sent connection confirmation to {video_id}")
                
                # Start monitoring the connection
                await self.monitor_connection(video_id, websocket)
                return
                
            except Exception as e:
                print(f"Error in WebSocket connection setup: {e}")
                await self.disconnect(video_id, websocket)
                
        except Exception as e:
            print(f"Error accepting WebSocket connection: {str(e)}")
            try:
                await websocket.close(code=1011, reason=f"Connection error: {str(e)}")
            except:
                pass

    async def monitor_connection(self, video_id: str, websocket: WebSocket):
        """Monitor WebSocket connection and clean up on disconnect"""
        if not websocket:
            print(f"WebSocket {video_id} is not valid")
            return
            
        try:
            while True:
                try:
                    # Wait for a message with a timeout
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    print(f"Received message from {video_id}: {data}")
                    
                    # Handle ping/pong
                    try:
                        message = json.loads(data)
                        if message.get("type") == "ping":
                            await websocket.send_json({
                                "type": "pong",
                                "timestamp": message.get("timestamp"),
                                "server_time": datetime.utcnow().isoformat()
                            })
                    except json.JSONDecodeError:
                        print(f"Received non-JSON message: {data}")
                    
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    try:
                        await websocket.send_json({
                            "type": "ping",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        print(f"Sent ping to {video_id}")
                    except Exception as e:
                        print(f"Failed to send ping to {video_id}: {str(e)}")
                        break
                        
                except WebSocketDisconnect as e:
                    print(f"WebSocket {video_id} was disconnected by client: {str(e)}")
                    break
                    
                except Exception as e:
                    print(f"Error in WebSocket monitor for {video_id}: {str(e)}")
                    break
                    
        except Exception as e:
            print(f"WebSocket monitor error for {video_id}: {str(e)}")
        finally:
            await self.disconnect(video_id, websocket)

    async def disconnect(self, video_id: str, websocket: WebSocket = None):
        """Disconnect a WebSocket connection"""
        if not video_id:
            return
            
        try:
            if video_id in self.active_connections:
                if websocket is None or self.active_connections[video_id] == websocket:
                    try:
                        # Try to close the connection
                        try:
                            await websocket.close(code=1000, reason="Client disconnected")
                        except Exception as e:
                            print(f"Error while closing WebSocket {video_id}: {str(e)}")
                    except Exception as e:
                        print(f"Error in WebSocket close for {video_id}: {str(e)}")
                    
                    # Remove from active connections
                    try:
                        if video_id in self.active_connections:
                            del self.active_connections[video_id]
                            print(f"WebSocket disconnected for video: {video_id}")
                    except Exception as e:
                        print(f"Error removing WebSocket {video_id} from active connections: {str(e)}")
        
        except Exception as e:
            print(f"Error in disconnect for {video_id}: {str(e)}")

    async def send_progress(self, video_id: str, data: dict):
        if video_id in self.active_connections:
            websocket = self.active_connections[video_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                print(f"Error sending progress update: {e}")
                self.disconnect(video_id)

manager = ConnectionManager()

# Simulated video generation stages
GENERATION_STAGES = [
    {"stage": "Analyzing prompt...", "progress": 0},
    {"stage": "Generating script...", "progress": 20},
    {"stage": "Creating scenes...", "progress": 40},
    {"stage": "Rendering video...", "progress": 60},
    {"stage": "Finalizing...", "progress": 80},
    {"stage": "Complete!", "progress": 100},
]

async def simulate_video_generation(video_id: str, request: VideoCreateRequest):
    """Simulate video generation process with progress updates"""
    try:
        for stage_info in GENERATION_STAGES:
            # Update video status
            videos_db[video_id]["status"] = "processing" if stage_info["progress"] < 100 else "completed"
            videos_db[video_id]["progress"] = stage_info["progress"]
            videos_db[video_id]["stage"] = stage_info["stage"]
            
            if stage_info["progress"] == 100:
                videos_db[video_id]["output_url"] = f"/api/videos/{video_id}/download"
            
            # Send WebSocket update
            await manager.send_progress(video_id, {
                "video_id": video_id,
                "status": videos_db[video_id]["status"],
                "progress": stage_info["progress"],
                "stage": stage_info["stage"],
                "output_url": videos_db[video_id].get("output_url")
            })
            
            # Simulate processing time
            await asyncio.sleep(2)
            
    except Exception as e:
        videos_db[video_id]["status"] = "failed"
        videos_db[video_id]["error"] = str(e)
        await manager.send_progress(video_id, {
            "video_id": video_id,
            "status": "failed",
            "error": str(e)
        })

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "OmniVid API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/videos/", response_model=VideoResponse)
@app.post("/api/videos/create", response_model=VideoResponse)
async def create_video(request: VideoCreateRequest):
    """Create a new video generation request"""
    video_id = str(uuid.uuid4())
    
    # Store video metadata
    videos_db[video_id] = {
        "video_id": video_id,
        "prompt": request.prompt,
        "settings": request.settings.dict(),
        "status": "queued",
        "progress": 0,
        "stage": "Initializing...",
        "created_at": datetime.utcnow().isoformat(),
        "output_url": None,
        "error": None
    }
    
    # Start generation in background
    asyncio.create_task(simulate_video_generation(video_id, request))
    
    return VideoResponse(
        id=video_id,
        video_id=video_id,
        status="queued",
        message="Video generation started",
        prompt=request.prompt,
        progress=0,
        current_stage="Initializing..."
    )

@app.get("/api/v1/videos/{video_id}", response_model=VideoStatus)
@app.get("/api/videos/{video_id}/status", response_model=VideoStatus)
async def get_video_status(video_id: str):
    """Get video generation status"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = videos_db[video_id]
    return VideoStatus(
        video_id=video_id,
        status=video["status"],
        progress=video["progress"],
        stage=video["stage"],
        output_url=video.get("output_url"),
        error=video.get("error")
    )

@app.get("/api/v1/videos/")
@app.get("/api/videos")
async def list_videos():
    """List all videos"""
    return {
        "videos": list(videos_db.values()),
        "total": len(videos_db),
        "page": 1,
        "page_size": len(videos_db)
    }

@app.delete("/api/v1/videos/{video_id}")
@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete a video"""
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    
    del videos_db[video_id]
    return {"message": "Video deleted successfully", "video_id": video_id}

@app.websocket("/api/v1/ws/videos/{video_id}")
@app.websocket("/ws/videos/{video_id}")
async def websocket_endpoint(websocket: WebSocket, video_id: str):
    """WebSocket endpoint for real-time progress updates"""
    # Let the ConnectionManager handle the connection
    await manager.connect(video_id, websocket)
    
    # Keep the connection alive
    try:
        while True:
            # Just keep the connection open
            # The actual message handling is done in monitor_connection
            await asyncio.sleep(1)
    except WebSocketDisconnect as e:
        print(f"Client disconnected: {e}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        # Ensure cleanup
        await manager.disconnect(video_id, websocket)

# Template endpoints
@app.get("/api/templates")
async def list_templates():
    """List available templates"""
    templates = [
        {
            "id": "modern",
            "name": "Modern Minimal",
            "description": "Clean and professional",
            "category": "business",
            "style": "modern"
        },
        {
            "id": "vibrant",
            "name": "Vibrant Energy",
            "description": "Bold and colorful",
            "category": "marketing",
            "style": "vibrant"
        },
        {
            "id": "cinematic",
            "name": "Cinematic",
            "description": "Movie-like quality",
            "category": "entertainment",
            "style": "cinematic"
        },
        {
            "id": "corporate",
            "name": "Corporate",
            "description": "Professional business",
            "category": "business",
            "style": "corporate"
        }
    ]
    return {"templates": templates}

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get template details"""
    # Placeholder - return template info
    return {
        "id": template_id,
        "name": f"Template {template_id}",
        "description": "Template description",
        "preview_url": f"/api/templates/{template_id}/preview"
    }

if __name__ == "__main__":
    print("🎬 Starting OmniVid Backend Server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔗 WebSocket: ws://localhost:8000/ws/videos/{video_id}")
    print("✨ Ready to create magic!\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
