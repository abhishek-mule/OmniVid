"""
AI-Video Generation API: Clean compiler-style pipeline.
POST /api/v1/generate - Convert prompt to Scene JSON to Code to Video.
GET /api/v1/status/:job_id - Check render status.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from pydantic import BaseModel, Field
import logging

from ...core.parser.llm_parser import parser
from ...core.jobs.dispatcher import job_dispatcher

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class PromptInput(BaseModel):
    """Natural language prompt for video generation."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language video description",
    )
    project_id: int | None = Field(None, description="Project to associate video with")
    settings: Dict[str, Any] | None = Field(
        default_factory=dict, description="Optional generation settings"
    )


class JobStatus(BaseModel):
    """Job render status."""

    job_id: str
    status: str
    progress: float
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result_path: str | None = None
    error: str | None = None


@router.post("/generate", response_model=JobStatus)
async def generate_video(request: PromptInput) -> JobStatus:
    """
    Generate video from natural language prompt using compiler pipeline.

    Pipeline:
    1. Parse prompt → Scene JSON
    2. Compile Scene JSON → Engine code
    3. Execute code → Raw video
    4. Stitch/optimize → Final video
    """
    try:
        logger.info(f"Starting video generation: {request.prompt[:50]}...")

        # Parse natural language to Scene JSON
        scene_json = parser.parse(request.prompt)

        # Generate unique job ID
        import uuid

        job_id = str(uuid.uuid4())

        # Submit to job dispatcher
        job_id = job_dispatcher.submit_job(
            prompt=request.prompt,
            scene_json=scene_json.to_dict(),
            output_path=f"./backend/storage/renders/{job_id}.mp4",
            priority=request.settings.get("priority", 1) if request.settings else 1,
        )

        return JobStatus(
            job_id=job_id,
            status="processing",
            progress=0,
            created_at=scene_json.metadata["parsed_at"],
        )

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}",
        )


@router.get("/status/{job_id}", response_model=JobStatus)
def get_job_status(job_id: str) -> JobStatus:
    """Get the status of a rendering job."""
    try:
        job_info = job_dispatcher.get_job_status(job_id)
        if not job_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )

        return JobStatus(
            job_id=job_info["job_id"],
            status=job_info["status"],
            progress=job_info["progress"],
            created_at=job_info["created_at"],
            started_at=job_info["started_at"],
            completed_at=job_info["completed_at"],
            result_path=(
                job_info.get("result", {}).get("output_path")
                if job_info.get("result")
                else None
            ),
            error=job_info.get("error"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job status",
        )
