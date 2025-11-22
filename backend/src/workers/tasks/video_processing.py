"""
Celery tasks for video processing in OmniVid.
"""

import json
import logging
import os
from datetime import datetime

from celery import current_task
from sqlalchemy.orm import Session

from src.config.settings import OUTPUT_DIR

# Import database repositories
from src.database.connection import SessionLocal
from src.database.repository import (
    AssetRepository,
    JobRepository,
    ProjectRepository,
    VideoRepository,
)
from src.database.schemas import VideoCreate

# Import WebSocket manager
from src.services.websocket_manager import connection_manager
from src.workers.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def generate_video(self, video_data: dict, user_id: int):
    """Celery task to generate a video."""
    db = SessionLocal()
    try:
        video_repo = VideoRepository(db)
        job_repo = JobRepository(db)

        video_id = video_data.get("video_id")
        if not video_id:
            raise ValueError("Video ID is required")

        # Get the video from database
        video = video_repo.get_video(video_id)
        if not video:
            raise ValueError(f"Video with ID {video_id} not found")

        # Update video status to processing
        video_repo.update_video_progress(video_id, 10, "processing")

        # Broadcast initial progress update
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=10,
            stage="Initializing",
            status="processing",
        )

        # Update Celery task progress
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 20,
                "total": 100,
                "status": "Setting up render environment",
            },
        )

        # Broadcast progress
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=20,
            stage="Setting up render environment",
            status="processing",
        )

        # Get project and verify access
        project_repo = ProjectRepository(db)
        project = project_repo.get_project(video.project_id)
        if not project or project.user_id != user_id:
            raise PermissionError("User does not have access to this project")

        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Preparing video assets"},
        )

        # Broadcast progress
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=30,
            stage="Preparing video assets",
            status="processing",
        )

        # Simulate video processing steps
        steps = [
            (40, "Analyzing prompt and generating storyboard"),
            (50, "Creating video scenes and animations"),
            (70, "Rendering video frames"),
            (85, "Applying post-processing effects"),
            (95, "Finalizing video output"),
        ]

        for progress, status in steps:
            # Update database progress
            video_repo.update_video_progress(video_id, progress, "processing")

            # Update Celery task progress
            current_task.update_state(
                state="PROGRESS",
                meta={"current": progress, "total": 100, "status": status},
            )

            # Broadcast progress via WebSocket
            connection_manager.broadcast_progress_update(
                video_id=str(video_id),
                progress=progress,
                stage=status,
                status="processing",
            )

            # Simulate work (in real implementation, this would be actual video processing)
            import time

            time.sleep(2)

        # Generate final video URL (in real implementation, this would be the actual rendered video)
        video_url = (
            f"/output/videos/{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        thumbnail_url = f"/output/thumbnails/{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        # Update video with completion data
        video_update = {
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "duration": 30.0,  # Example duration
            "status": "completed",
        }
        video_repo.update_video(video_id, video_update)
        video_repo.update_video_progress(video_id, 100, "completed")

        # Broadcast completion via WebSocket
        connection_manager.broadcast_completion(
            video_id=str(video_id), output_url=video_url, thumbnail_url=thumbnail_url
        )

        logger.info(f"Video {video_id} generation completed successfully")

        return {
            "video_id": video_id,
            "status": "completed",
            "video_url": video_url,
            "thumbnail_url": thumbnail_url,
            "duration": 30.0,
        }

    except Exception as e:
        logger.error(f"Video {video_id} generation failed: {str(e)}")

        # Update video status to failed
        if video_id:
            video_repo.update_video_progress(video_id, 0, "failed")
            video_repo.update_video(video_id, {"error_message": str(e)})

            # Broadcast error via WebSocket
            connection_manager.broadcast_progress_update(
                video_id=str(video_id),
                progress=0,
                stage="Error",
                status="failed",
                error=str(e),
            )

        raise
    finally:
        db.close()


@app.task(bind=True)
def render_video_blender(self, video_data: dict, user_id: int):
    """Celery task to render a video using Blender with process isolation."""
    from src.render_engines.blender.engine import BlenderRenderEngine

    db = SessionLocal()
    try:
        video_repo = VideoRepository(db)
        video_id = video_data.get("video_id")
        prompt = video_data.get("prompt", "default scene")
        settings = video_data.get("settings", {})

        # Get video information
        video = video_repo.get_video(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        # Broadcast initial progress
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=5,
            stage="Initializing Blender render engine",
            status="processing",
        )

        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 5,
                "total": 100,
                "status": "Initializing Blender render engine",
            },
        )

        # Initialize Blender Render Engine
        engine = BlenderRenderEngine()
        if not engine.initialize():
            raise RuntimeError("Failed to initialize Blender render engine")

        video_repo.update_video_progress(video_id, 10, "processing")
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=10,
            stage="Creating Blender scene (isolated process)",
            status="processing",
        )
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 10,
                "total": 100,
                "status": "Creating Blender scene (isolated process)",
            },
        )

        try:
            # Update settings with job ID for manifest
            settings['job_id'] = f"video_{video_id}"

            # Step 1: Create production-ready scene with manifest
            logger.info(f"Creating production scene for video {video_id} with prompt: {prompt}")
            blend_path = engine.create_scene(prompt, settings)

            video_repo.update_video_progress(video_id, 30, "processing")
            connection_manager.broadcast_progress_update(
                video_id=str(video_id),
                progress=30,
                stage="Production scene created (manifest validated)",
                status="processing",
            )
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 30,
                    "total": 100,
                    "status": "Production scene created (manifest validated)",
                },
            )

            # Step 2: Render video in isolated process with full validation
            output_path = f"{OUTPUT_DIR}/videos/{video_id}_blender.mp4"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            logger.info(f"Rendering production video {video_id} to: {output_path}")
            result = engine.render_video(blend_path, output_path)

            if not result.success:
                raise RuntimeError(f"Blender rendering failed: {result.error_message}")

            # Step 3: Post-render cleanup and artifact management
            video_repo.update_video_progress(video_id, 95, "processing")
            connection_manager.broadcast_progress_update(
                video_id=str(video_id),
                progress=95,
                stage="Render completed, cleaning up artifacts",
                status="processing",
            )

            # Clean up job-specific temporary files only (preserve .blend for debugging)
            try:
                from src.workers.jobs_cleanup import cleanup_job_artifacts_sync
                cleanup_job_artifacts_sync(video_id)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup failed for video {video_id}: {cleanup_error}")
                # Don't fail the whole render for cleanup issues

            # Update video with completion data
            video_update = {
                "video_url": f"/videos/{video_id}_blender.mp4",
                "thumbnail_url": f"/thumbnails/{video_id}_blender.jpg",  # Would generate actual thumbnail
                "duration": result.duration or 10.0,
                "status": "completed",
                "resolution": result.resolution or (1920, 1080),
            }
            video_repo.update_video(video_id, video_update)
            video_repo.update_video_progress(video_id, 100, "completed")

            # Broadcast completion
            connection_manager.broadcast_completion(
                video_id=str(video_id),
                output_url=video_update["video_url"],
                thumbnail_url=video_update["thumbnail_url"]
            )

            current_task.update_state(
                state="PROGRESS",
                meta={"current": 100, "total": 100, "status": "Completed"},
            )

            logger.info(f"Blender rendering completed for video {video_id}")
            return {
                "video_id": video_id,
                "engine": "blender",
                "status": "completed",
                "scene_path": blend_path,
                "output_path": output_path
            }

        except Exception as e:
            # Clean up on failure
            engine.cleanup()
            raise

    except Exception as e:
        logger.error(f"Blender rendering failed for video {video_id}: {str(e)}")

        # Update video status to failed
        video_repo.update_video_progress(video_id, 0, "failed")
        video_repo.update_video(video_id, {"error_message": str(e)})

        # Broadcast error
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=0,
            stage="Blender render failed",
            status="failed",
            error=str(e),
        )

        current_task.update_state(
            state="FAILED",
            meta={"error": str(e), "current": 0, "total": 100},
        )
        raise
    finally:
        db.close()


@app.task(bind=True)
def process_video_upload(self, asset_data: dict, user_id: int):
    """Celery task to process uploaded video files."""
    db = SessionLocal()
    try:
        video_repo = VideoRepository(db)
        asset_repo = AssetRepository(db)

        asset_id = asset_data.get("asset_id")
        video_id = asset_data.get("video_id")

        if not asset_id:
            raise ValueError("Asset ID is required")

        current_task.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Validating uploaded file"},
        )

        # Process the uploaded file
        processing_steps = [
            (40, "Analyzing video format"),
            (60, "Extracting metadata"),
            (80, "Generating thumbnails"),
            (95, "Optimizing for web"),
        ]

        for progress, status in processing_steps:
            current_task.update_state(
                state="PROGRESS",
                meta={"current": progress, "total": 100, "status": status},
            )

            # Broadcast progress if video_id is provided
            if video_id:
                connection_manager.broadcast_progress_update(
                    video_id=str(video_id),
                    progress=progress,
                    stage=status,
                    status="processing",
                )

            import time

            time.sleep(1)

        # Mark asset as processed
        asset_repo.update_asset_processing_status(
            asset_id,
            True,
            json.dumps(
                {
                    "processed_at": datetime.now().isoformat(),
                    "duration": 45.0,
                    "resolution": "1920x1080",
                    "format": "mp4",
                }
            ),
        )

        logger.info(f"Asset {asset_id} processing completed")

        return {"asset_id": asset_id, "status": "processed"}

    except Exception as e:
        logger.error(f"Asset processing failed: {str(e)}")
        if asset_id:
            asset_repo.update_asset_processing_status(asset_id, False)

        # Broadcast error if video_id is provided
        if video_id:
            connection_manager.broadcast_progress_update(
                video_id=str(video_id),
                progress=0,
                stage="Error",
                status="failed",
                error=str(e),
            )
        raise
    finally:
        db.close()


@app.task
def cleanup_old_jobs():
    """Periodic task to clean up old completed/failed jobs."""
    db = SessionLocal()
    try:
        from datetime import timedelta

        from sqlalchemy import and_

        # Clean up jobs older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)

        # This would be implemented in the JobRepository
        # For now, just log the cleanup task
        logger.info("Running job cleanup task")

        return {"cleaned_jobs": 0, "message": "Cleanup completed"}

    except Exception as e:
        logger.error(f"Job cleanup failed: {str(e)}")
        raise
    finally:
        db.close()


@app.task
def send_progress_update(video_id: int, progress: int, status: str, message: str = ""):
    """Send progress update via WebSocket."""
    try:
        connection_manager.broadcast_progress_update(
            video_id=str(video_id),
            progress=progress,
            stage=message or status,
            status=status,
        )
        return {
            "video_id": video_id,
            "progress": progress,
            "status": status,
            "message": message,
        }
    except Exception as e:
        logger.error(f"Failed to send progress update: {e}")
        return {"error": str(e)}
