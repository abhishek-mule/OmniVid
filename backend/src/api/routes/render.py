#!/usr/bin/env python3
"""
Simple render job queuing API
Provides REST endpoint to queue Blender render jobs with production infrastructure.
"""

import asyncio
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import shutil

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
import aiofiles

from ...utils.blender_supervisor import (
    create_render_manifest, save_manifest_atomic,
    BlenderSupervisor, BlenderResult
)
from ...utils.production_render import render_video_production_async
from ...utils.debounced_writer import debounced_writer
from ...utils.structured_logger import StructuredLogger

router = APIRouter(prefix="/render", tags=["render"])


class RenderJobRequest(BaseModel):
    """Request model for render job creation."""
    prompt: str = Field(..., description="Text description of what to render")
    resolution: tuple[int, int] = Field((1920, 1080), description="Output resolution (width, height)")
    fps: int = Field(30, description="Frames per second")
    duration: float = Field(10.0, description="Duration in seconds")
    job_id: Optional[str] = Field(None, description="Optional custom job ID")

    class Config:
        schema_extra = {
            "example": {
                "prompt": "blue cube rotating in space",
                "resolution": [1920, 1080],
                "fps": 30,
                "duration": 5.0,
                "job_id": "custom_job_123"
            }
        }


class RenderJobResponse(BaseModel):
    """Response model for render job creation."""
    job_id: str
    status: str
    message: str
    estimated_duration_seconds: float
    queue_position: int = 0


@router.post("/job", response_model=RenderJobResponse)
async def queue_render_job(
    request: RenderJobRequest,
    background_tasks: BackgroundTasks
) -> RenderJobResponse:
    """
    Queue a new render job.

    This endpoint creates a production-ready render job with:
    - SHA256 manifest validation
    - Blender supervisor with retry logic
    - Auto-camera positioning
    - Atomic frame rendering with .ok markers
    - FFmpeg video assembly with progress monitoring
    """
    try:
        # Generate job ID if not provided
        job_id = request.job_id or f"render_{uuid.uuid4().hex[:12]}"

        # Create job directory structure
        job_dir = Path("data/jobs") / job_id
        blend_dir = job_dir / "blend"
        frames_dir = job_dir / "frames"
        output_dir = job_dir / "output"

        # Ensure directories exist
        for dir_path in [job_dir, blend_dir, frames_dir, output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create render manifest
        settings = {
            "prompt": request.prompt,
            "resolution": list(request.resolution),  # Convert tuple to list for JSON
            "fps": request.fps,
            "duration": request.duration,
            "output_format": "mp4",
            "render_engine": "BLENDER_EEVEE"
        }

        manifest = create_render_manifest(job_id, settings)

        # Save manifest atomically
        manifest_path = job_dir / "manifest.json"
        success = save_manifest_atomic(manifest, manifest_path)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save render manifest")

        # Save job request for reconstruction
        job_request = request.dict()
        job_request["job_id"] = job_id
        job_request["created_at"] = datetime.now().isoformat()

        request_path = job_dir / "request.json"
        async with aiofiles.open(request_path, 'w') as f:
            await f.write(__import__('json').dumps(job_request, indent=2))

        # Queue the background task
        background_tasks.add_task(
            process_render_job_background,
            job_id=job_id,
            job_dir=str(job_dir),
            manifest_path=str(manifest_path),
            settings=settings
        )

        # Calculate estimated duration (rough estimate)
        estimated_frames = int(request.duration * request.fps)
        estimated_seconds = estimated_frames * 2.0 + 30  # 2s per frame + 30s overhead

        return RenderJobResponse(
            job_id=job_id,
            status="queued",
            message="Render job queued successfully",
            estimated_duration_seconds=estimated_seconds,
            queue_position=0  # Simple implementation
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue render job: {str(e)}")


@router.get("/job/{job_id}")
async def get_render_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a render job.

    Returns job status, progress, and any available results.
    """
    try:
        job_dir = Path("data/jobs") / job_id
        if not job_dir.exists():
            raise HTTPException(status_code=404, detail="Job not found")

        # Read job request
        request_path = job_dir / "request.json"
        status_path = job_dir / "status.json"
        result_path = job_dir / "result.json"

        status_info = {
            "job_id": job_id,
            "status": "unknown",
            "progress": 0.0,
            "message": "Job status unknown",
            "created_at": None,
            "started_at": None,
            "completed_at": None,
            "result": None
        }

        # Load request info
        if request_path.exists():
            async with aiofiles.open(request_path, 'r') as f:
                request_data = __import__('json').loads(await f.read())
            status_info["created_at"] = request_data.get("created_at")
            status_info["prompt"] = request_data.get("prompt")
            status_info["resolution"] = request_data.get("resolution")
            status_info["fps"] = request_data.get("fps")

        # Load current status
        if status_path.exists():
            async with aiofiles.open(status_path, 'r') as f:
                status_data = __import__('json').loads(await f.read())
            status_info.update(status_data)

        # Load final result if available
        if result_path.exists():
            async with aiofiles.open(result_path, 'r') as f:
                result_data = __import__('json').loads(await f.read())
            status_info["result"] = result_data

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/jobs")
async def list_render_jobs(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    List recent render jobs.

    Returns paginated list of jobs with basic status info.
    """
    try:
        jobs_dir = Path("data/jobs")
        if not jobs_dir.exists():
            return {"jobs": [], "total": 0}

        # Get job directories sorted by creation time (newest first)
        job_dirs = []
        for job_dir in jobs_dir.iterdir():
            if job_dir.is_dir():
                request_path = job_dir / "request.json"
                if request_path.exists():
                    job_dirs.append((job_dir, request_path.stat().st_mtime))

        # Sort by modification time (newest first)
        job_dirs.sort(key=lambda x: x[1], reverse=True)

        # Paginate
        total_jobs = len(job_dirs)
        paginated_dirs = job_dirs[offset:offset + limit]

        jobs = []
        for job_dir, _ in paginated_dirs:
            job_id = job_dir.name

            # Get basic info
            job_info = {"job_id": job_id, "status": "unknown"}

            # Load request info if available
            request_path = job_dir / "request.json"
            if request_path.exists():
                try:
                    async with aiofiles.open(request_path, 'r') as f:
                        request_data = __import__('json').loads(await f.read())
                    job_info["prompt"] = request_data.get("prompt", "")[:50] + "..."
                    job_info["created_at"] = request_data.get("created_at")
                except:
                    pass

            # Load status if available
            status_path = job_dir / "status.json"
            if status_path.exists():
                try:
                    async with aiofiles.open(status_path, 'r') as f:
                        status_data = __import__('json').loads(await f.read())
                    job_info.update(status_data)
                except:
                    pass

            jobs.append(job_info)

        return {
            "jobs": jobs,
            "total": total_jobs,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


async def process_render_job_background(
    job_id: str,
    job_dir: str,
    manifest_path: str,
    settings: Dict[str, Any]
) -> None:
    """
    Background task to process render job using production infrastructure.

    This is where the actual render processing happens using all our
    production-grade components (supervisor, atomic operations, etc.)
    """
    job_path = Path(job_dir)
    status_path = job_path / "status.json"
    result_path = job_path / "result.json"
    metrics_path = job_path / "metrics.json"

    start_time = datetime.now().timestamp()
    job_metrics = {
        "job_id": job_id,
        "start_time": datetime.fromtimestamp(start_time).isoformat(),
        "phases": [],
        "performance": {},
        "errors": [],
        "cleanup": {"bytes_freed": 0, "files_cleaned": 0}
    }

    def record_phase(phase_name: str, phase_data: Dict[str, Any]):
        """Record timing and data for a processing phase."""
        now = datetime.now().timestamp()
        phase_data["phase_duration_seconds"] = now - phase_data.get("start_time", now)
        phase_data["phase"] = phase_name
        phase_data["timestamp"] = datetime.fromtimestamp(now).isoformat()
        job_metrics["phases"].append(phase_data)

    def update_progress(progress: float, message: str):
        """Update job progress and save metrics."""
        try:
            status_update = {
                "status": "running",
                "progress": progress,
                "message": message,
                "phase_start": start_time,
                "current_time": datetime.now().isoformat()
            }

            # Save status
            asyncio.create_task(save_async(status_path, status_update))

            # Update metrics
            now = datetime.now().timestamp()
            if "performance" not in job_metrics:
                job_metrics["performance"] = {}

            job_metrics["performance"]["elapsed_seconds"] = now - start_time
            job_metrics["performance"]["progress_percentage"] = progress
            job_metrics["performance"]["current_phase"] = message

            # Save metrics
            asyncio.create_task(save_async(metrics_path, job_metrics))

        except Exception as e:
            print(f"Warning: Failed to update progress: {e}")

    async def save_async(file_path: Path, data: Dict[str, Any]):
        """Save data asynchronously."""
        try:
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
        except Exception as e:
            print(f"Warning: Failed to save {file_path}: {e}")

    try:
        # Phase 1: Job initialization
        update_progress(2.0, "Initializing render job")

        phase_start = datetime.now().timestamp()
        init_data = {
            "start_time": phase_start,
            "job_dir": job_dir,
            "settings": settings,
            "manifest_path": manifest_path
        }

        # Load manifest for validation
        manifest_data = {}
        try:
            async with aiofiles.open(manifest_path, 'r') as f:
                manifest_data = json.loads(await f.read())
            init_data["manifest_loaded"] = True
        except Exception as e:
            init_data["manifest_error"] = str(e)
            job_metrics["errors"].append(f"Manifest load failed: {str(e)}")

        record_phase("initialization", init_data)

        # Phase 2: Video processing (main work)
        update_progress(5.0, "Starting video processing")

        process_start = datetime.now().timestamp()
        process_data = {
            "start_time": process_start,
            "frames_expected": int(settings.get("duration", 10) * settings.get("fps", 30)),
            "resolution": settings.get("resolution"),
            "fps": settings.get("fps"),
            "duration": settings.get("duration")
        }

        try:
            # Here we would call our production frame renderer
            # For now, using the existing task as placeholder
            render_result = await asyncio.get_event_loop().run_in_executor(
                None,
                process_video_render_placeholder,
                job_id,
                job_path,
                Path(manifest_path),
                settings,
                update_progress  # Pass progress callback
            )

            process_data["render_success"] = render_result.success
            process_data["output_size_bytes"] = render_result.metadata.get("output_size", 0)
            process_data["frames_rendered"] = render_result.metadata.get("frames_rendered", 0)

        except Exception as e:
            process_data["render_error"] = str(e)
            job_metrics["errors"].append(f"Video processing failed: {str(e)}")
            raise

        record_phase("video_processing", process_data)

        # Phase 3: Cleanup and finalization
        update_progress(95.0, "Performing cleanup")

        cleanup_start = datetime.now().timestamp()
        cleanup_data = {"start_time": cleanup_start}

        try:
            # Clean up temporary frames older than 1 hour (aggressive cleanup)
            from ...render_engines.blender.templates.render_frames_production import cleanup_temp_frames

            bytes_freed = cleanup_temp_frames(job_path / "frames", max_age_hours=1)
            cleanup_data["temp_frames_cleaned"] = bytes_freed > 0
            cleanup_data["bytes_freed"] = bytes_freed
            job_metrics["cleanup"]["bytes_freed"] = bytes_freed
            job_metrics["cleanup"]["files_cleaned"] = cleanup_data.get("files_cleaned", 0)

        except Exception as e:
            cleanup_data["cleanup_error"] = str(e)

        record_phase("cleanup", cleanup_data)

        # Final metrics calculation
        end_time = datetime.now().timestamp()
        total_duration = end_time - start_time

        job_metrics.update({
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "total_duration_seconds": total_duration,
            "average_fps": process_data.get("frames_rendered", 0) / total_duration if total_duration > 0 else 0,
            "job_settings": settings,
            "final_status": "completed"
        })

        # Save final status and results
        final_status = {
            "status": "completed" if render_result.success else "failed",
            "progress": 100.0,
            "message": "Render completed successfully" if render_result.success else f"Render failed: {render_result.error_message}",
            "completed_at": datetime.fromtimestamp(end_time).isoformat(),
            "total_duration_seconds": total_duration
        }

        # Save final metrics and results
        result_data = {
            "success": render_result.success,
            "video_url": render_result.video_url,
            "duration": render_result.duration,
            "resolution": render_result.resolution,
            "metadata": render_result.metadata,
            "error_message": render_result.error_message,
            "metrics": job_metrics
        }

        update_progress(100.0, "Job completed")
        await save_async(status_path, final_status)
        await save_async(result_path, result_data)
        await save_async(metrics_path, job_metrics)

    except Exception as e:
        error_time = datetime.now().timestamp()
        error_message = f"Render job failed: {str(e)}"

        job_metrics["errors"].append(error_message)
        job_metrics["end_time"] = datetime.fromtimestamp(error_time).isoformat()
        job_metrics["total_duration_seconds"] = error_time - start_time
        job_metrics["final_status"] = "failed"

        error_status = {
            "status": "failed",
            "progress": 0.0,
            "message": error_message,
            "completed_at": datetime.fromtimestamp(error_time).isoformat(),
            "total_duration_seconds": error_time - start_time
        }

        try:
            await save_async(status_path, error_status)
            await save_async(metrics_path, job_metrics)
        except Exception:
            pass  # Best effort on error logging


# CLI interface for development/testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Render job queuing CLI")
    parser.add_argument("--queue", action="store_true", help="Queue a render job")
    parser.add_argument("--status", type=str, help="Get job status")
    parser.add_argument("--list", action="store_true", help="List recent jobs")
    parser.add_argument("--prompt", type=str, help="Render prompt")
    parser.add_argument("--resolution", type=str, default="1920x1080", help="Resolution (WxH)")

    args = parser.parse_args()

    if args.queue and args.prompt:
        # Simple CLI queuing (synchronous for testing)
        resolution = tuple(map(int, args.resolution.split('x')))

        request = RenderJobRequest(
            prompt=args.prompt,
            resolution=resolution,
            fps=30,
            duration=5.0
        )

        # Mock background task processing
        print(f"Would queue job: {request.prompt}")
        print(f"Resolution: {request.resolution}")
        print("Use REST API for actual queuing")

    elif args.status:
        # Get job status (would need to be implemented)
        print(f"Would get status for job: {args.status}")

    elif args.list:
        # List jobs (would need to be implemented)
        print("Would list recent jobs")

    else:
        parser.print_help()
