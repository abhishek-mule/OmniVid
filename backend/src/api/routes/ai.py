"""
AI-powered video generation API routes.
Provides endpoints for natural language to video conversion using OmniVid Lite.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from ...database.connection import get_db
from ...database.repository import ProjectRepository, VideoRepository
from ...database.schemas import VideoCreate
from ...auth.security import get_current_user
from ...services.render_pipeline import render_pipeline
from ...services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class AIVideoRequest(BaseModel):
    """Request model for AI video generation."""

    prompt: str = Field(
        ...,
        description="Natural language description of the video to generate",
        min_length=1,
        max_length=1000,
    )
    project_id: int = Field(..., description="Project ID to associate the video with")
    title: Optional[str] = Field(None, description="Optional title for the video")
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional rendering settings"
    )


class AIVideoResponse(BaseModel):
    """Response model for AI video generation requests."""

    video_id: int
    job_id: str
    status: str = "processing"
    message: str = "AI video generation started successfully"
    estimated_duration: Optional[float] = None


class VideoStatusResponse(BaseModel):
    """Response model for video status inquiries."""

    video_id: int
    status: str
    progress: float
    job_id: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=AIVideoResponse)
async def generate_ai_video(
    request: AIVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a video from natural language prompt using AI."""
    try:
        # Verify project ownership
        project_repo = ProjectRepository(db)
        project = project_repo.get_project(request.project_id)

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        if project.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create videos in this project",
            )

        # Create video record in database
        video_create = VideoCreate(
            project_id=request.project_id,
            title=request.title or f"AI Generated: {request.prompt[:50]}...",
            status="processing",
            prompt=request.prompt,
            settings=request.settings or {},
        )

        video_repo = VideoRepository(db)
        video = video_repo.create_video(video_create)

        # Set up output path
        output_filename = f"ai_video_{video.id}.mp4"
        output_path = f"./backend/uploads/videos/{output_filename}"

        # Ensure output directory exists
        import os

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Progress callback function
        def progress_callback(progress: float, status: str, message: str):
            try:
                # Update video progress in database
                progress_percentage = min(max(progress, 0), 100)
                updated_video = video_repo.update_video_progress(
                    video.id, progress_percentage / 100.0, status.lower()
                )

                # Send WebSocket update to client
                try:
                    websocket_manager.broadcast_to_user(
                        current_user["user_id"],
                        {
                            "type": "video_progress",
                            "video_id": video.id,
                            "progress": progress_percentage,
                            "status": status.lower(),
                            "message": message,
                        },
                    )
                except Exception as ws_error:
                    logger.warning(f"WebSocket broadcast failed: {ws_error}")

            except Exception as e:
                logger.error(f"Failed to update progress for video {video.id}: {e}")

        # Start AI video generation in background
        async def start_ai_generation():
            try:
                # Use the AI service to generate video
                job_id = await render_pipeline.start_ai_render(
                    prompt=request.prompt,
                    output_path=output_path,
                    progress_callback=progress_callback,
                )

                # Update video with job_id
                video_repo.update_video_job_id(video.id, job_id)

                logger.info(
                    f"Started AI video generation for video {video.id}, job {job_id}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to start AI video generation for video {video.id}: {e}"
                )

                # Update video status to failed
                try:
                    video_repo.update_video_progress(video.id, 0, "failed")
                    video_repo.update_video_error(video.id, str(e))
                except Exception as update_error:
                    logger.error(f"Failed to update video error status: {update_error}")

        # Start the background task
        background_tasks.add_task(start_ai_generation)

        # Estimate duration based on prompt complexity
        estimated_duration = len(request.prompt.split()) * 2.0  # Rough estimate

        return AIVideoResponse(
            video_id=video.id,
            job_id="",  # Will be set asynchronously
            status="processing",
            message="AI video generation started. You will receive progress updates via WebSocket.",
            estimated_duration=estimated_duration,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI video generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start AI video generation",
        )


@router.get("/videos/{video_id}/status", response_model=VideoStatusResponse)
def get_ai_video_status(
    video_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the status of an AI-generated video."""
    try:
        # Verify video ownership
        video_repo = VideoRepository(db)
        video = video_repo.get_video(video_id)

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        # Check project ownership
        project_repo = ProjectRepository(db)
        project = project_repo.get_project(video.project_id)

        if project.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this video",
            )

        # Get additional status from render pipeline if job_id exists
        ai_metadata = None
        if video.job_id:
            job_status = render_pipeline.get_render_status(video.job_id)
            if job_status:
                # Extract AI-specific metadata
                settings = job_status.get("settings", {})
                ai_spec = settings.get("ai_spec")
                if ai_spec:
                    ai_metadata = {
                        "scene_type": ai_spec.get("scene_type"),
                        "engine_used": job_status.get("engine_type"),
                        "parameters": ai_spec.get("parameters", {}),
                    }

        return VideoStatusResponse(
            video_id=video.id,
            status=video.status,
            progress=video.progress * 100,  # Convert to percentage
            job_id=video.job_id,
            created_at=video.created_at.isoformat() if video.created_at else None,
            completed_at=video.completed_at.isoformat() if video.completed_at else None,
            error_message=video.error_message,
            ai_metadata=ai_metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AI video status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get video status",
        )


@router.post("/videos/{video_id}/retry")
def retry_ai_video_generation(
    video_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retry AI video generation for a failed video."""
    try:
        # Verify video ownership
        video_repo = VideoRepository(db)
        video = video_repo.get_video(video_id)

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
            )

        # Check project ownership
        project_repo = ProjectRepository(db)
        project = project_repo.get_project(video.project_id)

        if project.user_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to retry this video",
            )

        # Only allow retry for failed videos
        if video.status != "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only retry failed videos",
            )

        # Reset video status
        video_repo.update_video_progress(video_id, 0, "processing")
        video_repo.update_video_error(video_id, None)

        # Set up output path
        output_filename = f"ai_video_{video.id}.mp4"
        output_path = f"./backend/uploads/videos/{output_filename}"

        # Retry generation in background
        async def retry_generation():
            try:
                job_id = await render_pipeline.start_ai_render(
                    prompt=video.prompt,
                    output_path=output_path,
                    progress_callback=lambda p, s, m: video_repo.update_video_progress(
                        video_id, p / 100.0, s.lower()
                    ),
                )

                video_repo.update_video_job_id(video.id, job_id)
                logger.info(f"Retried AI video generation for video {video.id}")

            except Exception as e:
                logger.error(f"Retry failed for video {video.id}: {e}")
                video_repo.update_video_progress(video.id, 0, "failed")
                video_repo.update_video_error(video.id, f"Retry failed: {str(e)}")

        background_tasks.add_task(retry_generation)

        return {"message": "AI video generation retry started", "video_id": video_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying AI video generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry video generation",
        )


@router.get("/engines")
def get_available_ai_engines(current_user: dict = Depends(get_current_user)):
    """Get information about available AI rendering engines."""
    try:
        engines = render_pipeline.get_available_engines()
        return {
            "engines": engines,
            "supported_features": {
                "natural_language": True,
                "code_generation": True,
                "multi_engine": True,
                "real_time_progress": True,
            },
        }
    except Exception as e:
        logger.error(f"Error getting available engines: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available engines",
        )


@router.get("/capabilities")
def get_ai_capabilities(current_user: dict = Depends(get_current_user)):
    """Get AI video generation capabilities and supported formats."""
    return {
        "supported_engines": ["remotion", "manim", "ffmpeg"],
        "supported_scenes": ["text", "math", "animation", "web"],
        "max_prompt_length": 1000,
        "supported_resolutions": ["720p", "1080p", "4K"],
        "estimated_generation_time": "10-60 seconds",
        "features": [
            "Natural language processing",
            "Intelligent scene detection",
            "Code generation for animation engines",
            "Multi-engine orchestration",
            "Real-time progress updates",
        ],
    }
