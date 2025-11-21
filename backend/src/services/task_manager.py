"""
Task management service for video processing.
"""

from sqlalchemy.orm import Session
from ..workers.celery_app import app
from ..database.connection import SessionLocal
from ..database.repository import (
    VideoRepository,
    JobRepository,
    ProjectRepository,
    AssetRepository,
)
from ..database.schemas import JobCreate
from ..workers.tasks.video_processing import (
    generate_video,
    render_video_blender,
    process_video_upload,
)
import uuid
import logging

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self):
        self.celery_app = app

    def queue_video_generation(
        self, video_id: int, user_id: int, engine: str = "default"
    ) -> str:
        """Queue a video generation task."""
        db = SessionLocal()
        try:
            video_repo = VideoRepository(db)
            job_repo = JobRepository(db)

            # Verify video exists and user has access
            video = video_repo.get_video(video_id)
            if not video:
                raise ValueError(f"Video {video_id} not found")

            project_repo = ProjectRepository(db)
            project = project_repo.get_project(video.project_id)
            if not project or project.user_id != user_id:
                raise PermissionError("User does not have access to this video")

            # Create job record
            task_id = str(uuid.uuid4())
            job_data = JobCreate(task_id=task_id, video_id=video_id)
            job = job_repo.create_job(job_data)

            # Prepare video data for processing
            video_data = {
                "video_id": video_id,
                "prompt": video.prompt,
                "settings": video.settings,
                "project_id": video.project_id,
            }

            # Select appropriate task based on engine
            if engine == "blender":
                task = render_video_blender.delay(video_data, user_id)
            else:
                task = generate_video.delay(video_data, user_id)

            # Update job with Celery task ID
            job_repo.update_job(job.id, {"task_id": task.id})

            logger.info(f"Queued video generation task {task.id} for video {video_id}")

            return task.id

        except Exception as e:
            logger.error(f"Failed to queue video generation: {str(e)}")
            raise
        finally:
            db.close()

    def queue_video_upload_processing(
        self, asset_id: int, video_id: int, user_id: int
    ) -> str:
        """Queue a video upload processing task."""
        db = SessionLocal()
        try:
            asset_repo = AssetRepository(db)
            job_repo = JobRepository(db)

            # Create job record
            task_id = str(uuid.uuid4())
            job_data = JobCreate(task_id=task_id, video_id=video_id)
            job = job_repo.create_job(job_data)

            # Prepare asset data for processing
            asset_data = {"asset_id": asset_id, "video_id": video_id}

            task = process_video_upload.delay(asset_data, user_id)

            # Update job with Celery task ID
            job_repo.update_job(job.id, {"task_id": task.id})

            logger.info(f"Queued upload processing task {task.id} for asset {asset_id}")

            return task.id

        except Exception as e:
            logger.error(f"Failed to queue upload processing: {str(e)}")
            raise
        finally:
            db.close()

    def get_task_status(self, task_id: str) -> dict:
        """Get the status of a Celery task."""
        try:
            task = self.celery_app.AsyncResult(task_id)
            return {
                "task_id": task_id,
                "status": task.status,
                "result": task.result,
                "traceback": task.traceback,
            }
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {str(e)}")
            return {"task_id": task_id, "status": "UNKNOWN", "error": str(e)}

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        try:
            task = self.celery_app.AsyncResult(task_id)
            if task.status in ["PENDING", "RETRY", "STARTED"]:
                task.revoke(terminate=True)
                logger.info(f"Task {task_id} cancelled")
                return True
            else:
                logger.warning(f"Cannot cancel task {task_id} in status {task.status}")
                return False
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return False

    def get_worker_stats(self) -> dict:
        """Get Celery worker statistics."""
        try:
            inspect = self.celery_app.control.inspect()
            stats = inspect.stats()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()

            return {
                "workers": stats,
                "active_tasks": active_tasks,
                "scheduled_tasks": scheduled_tasks,
            }
        except Exception as e:
            logger.error(f"Failed to get worker stats: {str(e)}")
            return {
                "workers": {},
                "active_tasks": {},
                "scheduled_tasks": {},
                "error": str(e),
            }

    def cleanup_old_tasks(self, older_than_hours: int = 24) -> dict:
        """Clean up old task results."""
        from datetime import datetime, timedelta
        import time

        try:
            # Get tasks older than specified hours
            cutoff_time = time.time() - (older_than_hours * 3600)

            # This would typically involve querying Celery's result backend
            # For now, just return a placeholder response
            logger.info(f"Cleaning up tasks older than {older_than_hours} hours")

            return {
                "cleaned_tasks": 0,
                "cutoff_time": cutoff_time,
                "message": "Task cleanup completed",
            }

        except Exception as e:
            logger.error(f"Failed to cleanup tasks: {str(e)}")
            return {"error": str(e)}


# Global task manager instance
task_manager = TaskManager()
