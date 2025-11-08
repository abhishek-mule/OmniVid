"""
OMNIVID Backend API

FastAPI application for video generation orchestration.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from pathlib import Path

from config import settings, ensure_directories
from celery_app import render_remotion_video, get_render_status, cancel_render_task, health_check


# Pydantic models for request/response validation
class AssetConfig(BaseModel):
    """Asset configuration."""
    path: str = Field(..., description="Path to asset file")
    type: str = Field(..., description="Asset type (image, video, audio, etc.)")
    id: Optional[str] = Field(None, description="Optional asset ID")


class SceneConfig(BaseModel):
    """Scene configuration."""
    id: Optional[str] = Field(None, description="Scene ID")
    name: str = Field(..., description="Scene name")
    duration: float = Field(..., description="Scene duration in seconds")
    layers: List[Dict[str, Any]] = Field(default_factory=list, description="Scene layers")
    transitions: Optional[Dict[str, Any]] = Field(None, description="Transition effects")
    animations: Optional[Dict[str, Any]] = Field(None, description="Animation configs")


class RenderRequest(BaseModel):
    """Video render request."""
    remotion_root: Optional[str] = Field(None, description="Path to Remotion project")
    composition_id: Optional[str] = Field(None, description="Remotion composition ID")
    output_filename: str = Field(..., description="Output filename")
    width: int = Field(1920, description="Video width")
    height: int = Field(1080, description="Video height")
    fps: int = Field(30, description="Frame rate")
    quality: str = Field("high", description="Quality preset (low, medium, high, ultra)")
    format: str = Field("mp4", description="Output format")
    codec: Optional[str] = Field(None, description="Video codec")
    duration: Optional[float] = Field(None, description="Video duration")
    scenes: List[SceneConfig] = Field(default_factory=list, description="Scene configurations")
    assets: List[AssetConfig] = Field(default_factory=list, description="Asset configurations")
    additional_params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class RenderResponse(BaseModel):
    """Video render response."""
    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class TaskStatusResponse(BaseModel):
    """Task status response."""
    task_id: str
    state: str
    status: Dict[str, Any]
    ready: bool
    successful: Optional[bool]


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered video generation and orchestration API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    ensure_directories()
    print(f"{settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"Server running on {settings.HOST}:{settings.PORT}")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "omnivid-api"
    }


@app.get("/health/celery", tags=["Health"])
async def celery_health():
    """Check Celery worker health."""
    try:
        result = health_check.apply_async()
        response = result.get(timeout=5)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Celery workers unavailable: {str(e)}"
        )


@app.post("/render", response_model=RenderResponse, tags=["Rendering"])
async def render_video(request: RenderRequest):
    """
    Submit a video rendering job.
    
    This endpoint queues a video render job using Celery and returns
    a task ID that can be used to check the render status.
    """
    try:
        # Convert request to dict
        render_data = request.model_dump()
        
        # Queue render task
        task = render_remotion_video.apply_async(args=[render_data])
        
        return RenderResponse(
            task_id=task.id,
            status="queued",
            message="Render job queued successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue render job: {str(e)}"
        )


@app.get("/render/{task_id}", response_model=TaskStatusResponse, tags=["Rendering"])
async def get_render_status_endpoint(task_id: str):
    """
    Get the status of a render job.
    
    Returns the current state of the render task including progress
    information if available.
    """
    try:
        from celery.result import AsyncResult
        from celery_app import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        response_data = {
            "task_id": task_id,
            "state": result.state,
            "status": result.info if isinstance(result.info, dict) else {},
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else None
        }
        
        return TaskStatusResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@app.delete("/render/{task_id}", tags=["Rendering"])
async def cancel_render(task_id: str):
    """
    Cancel a render job.
    
    Attempts to cancel a running or queued render task.
    """
    try:
        result = cancel_render_task.apply_async(args=[task_id])
        response = result.get(timeout=5)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task: {str(e)}"
        )


@app.get("/render/{task_id}/result", tags=["Rendering"])
async def get_render_result(task_id: str):
    """
    Get the result of a completed render job.
    
    Returns the final render result including output path and metadata.
    """
    try:
        from celery.result import AsyncResult
        from celery_app import celery_app
        
        result = AsyncResult(task_id, app=celery_app)
        
        if not result.ready():
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Render job still in progress"
            )
        
        if result.failed():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Render job failed"
            )
        
        return result.result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get render result: {str(e)}"
        )


@app.get("/download/{filename}", tags=["Files"])
async def download_video(filename: str):
    """
    Download a rendered video file.
    
    Returns the video file if it exists in the output directory.
    """
    try:
        file_path = Path(settings.OUTPUT_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type="video/mp4",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )


@app.get("/outputs", tags=["Files"])
async def list_outputs():
    """
    List all rendered video files.
    
    Returns a list of available output files with metadata.
    """
    try:
        output_dir = Path(settings.OUTPUT_DIR)
        files = []
        
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created": file_path.stat().st_ctime,
                    "modified": file_path.stat().st_mtime
                })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list outputs: {str(e)}"
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
