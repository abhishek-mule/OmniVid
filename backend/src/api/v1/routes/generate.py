"""
AI-Video Generation API: Clean compiler-style pipeline.
POST /api/v1/generate - Convert prompt to Scene JSON to Code to Video.
GET /api/v1/status/:job_id - Check render status.
GET /api/v1/history - User's video history.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
from pathlib import Path
import asyncio

from ...core.parser.llm_parser import parser
from ...core.compiler.remotion_compiler import remotion_compiler
from ...core.orchestrator.ffmpeg_stitcher import ffmpeg_stitcher
from ...core.jobs.dispatcher import job_dispatcher, Job
from ...database.connection import get_db
from ...database.repository import ProjectRepository, VideoRepository
from ...auth.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class PromptInput(BaseModel):
    """Natural language prompt for video generation."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Natural language video description")
    project_id: Optional[int] = Field(None, description="Project to associate video with")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional generation settings")

class TemplateSelect(BaseModel):
    """Pre-defined video template selection."""
    template_id: str = Field(..., description="Template identifier")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Template customizations")

class JobStatus(BaseModel):
    """Job render status."""
    job_id: str
    status: str
    progress: float
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_path: Optional[str] = None
    error: Optional[str] = None

class RenderResult(BaseModel):
    """Completed render result."""
    job_id: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration: float
    resolution: str
    file_size: int

# Global storage for temp files (in production, use proper storage)
STORAGE_DIR = Path("./backend/storage")
RENDERS_DIR = STORAGE_DIR / "renders"
SCENES_DIR = STORAGE_DIR / "scenes"

# Ensure directories exist
RENDERS_DIR.mkdir(parents=True, exist_ok=True)
SCENES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/generate", response_model=JobStatus)
async def generate_video(
    request: PromptInput,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate video from natural language prompt using compiler pipeline.

    Pipeline:
    1. Parse prompt → Scene JSON
    2. Compile Scene JSON → Engine code
    3. Execute code → Raw video
    4. Stitch/optimize → Final video
    """
    try:
        logger.info(f"Starting video generation for user {current_user['user_id']}: {request.prompt[:50]}...")

        # Step 1: Parse natural language to Scene JSON
        logger.info("Step 1: Parsing prompt to Scene JSON")
        scene_json = parser.parse(request.prompt)

        # Add user context
        scene_json.metadata.update({
            "user_id": current_user["user_id"],
            "project_id": request.project_id,
            "custom_settings": request.settings
        })

        # Step 2: Generate unique job paths
        from ...core.utils.id_generator import generate_id
        job_id = generate_id("job")
        render_path = RENDERS_DIR / f"{job_id}.mp4"
        scene_dir = SCENES_DIR / job_id

        logger.info(f"Job {job_id}: Generated paths - render: {render_path}, scenes: {scene_dir}")

        # Step 3: Submit to job dispatcher (this will trigger the full pipeline)
        job_id = job_dispatcher.submit_job(
            prompt=request.prompt,
            scene_json=scene_json.to_dict(),
            output_path=str(render_path),
            priority=request.settings.get("priority", 1)
        )

        # Step 4: Store in database
        video_repo = VideoRepository(db)
        video_data = {
            "project_id": request.project_id or 1,  # Default project
            "title": f"AI Generated: {request.prompt[:50]}...",
            "status": "processing",
            "prompt": request.prompt,
            "settings": request.settings,
            "job_id": job_id
        }
        video = video_repo.create_video(video_data)

        logger.info(f"Created database record for video {video.id}, job {job_id}")

        return JobStatus(
            job_id=job_id,
            status="processing",
            progress=0,
            created_at=scene_json.metadata["parsed_at"]
        )

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a rendering job."""
    try:
        job_info = job_dispatcher.get_job_status(job_id)
        if not job_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

        # Verify ownership (in production, check if user owns this job)
        # For now, allow access since we don't have user-job association

        return JobStatus(
            job_id=job_info["job_id"],
            status=job_info["status"],
            progress=job_info["progress"],
            created_at=job_info["created_at"],
            started_at=job_info["started_at"],
            completed_at=job_info["completed_at"],
            result_path=job_info.get("result", {}).get("output_path") if job_info.get("result") else None,
            error=job_info
