"""
Render engine abstraction layer for OmniVid.
"""

import json
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RenderEngineType(Enum):
    BLENDER = "blender"
    FFMPEG = "ffmpeg"
    MANIM = "manim"
    REMOTION = "remotion"


class RenderStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RENDERING = "rendering"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderResult:
    def __init__(
        self,
        success: bool,
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        duration: Optional[float] = None,
        resolution: Optional[tuple] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.duration = duration
        self.resolution = resolution
        self.error_message = error_message
        self.metadata = metadata or {}
        self.timestamp = None  # Would be set by actual implementation


class RenderJob:
    def __init__(
        self,
        job_id: str,
        engine_type: RenderEngineType,
        prompt: str,
        settings: Dict[str, Any],
        output_path: str,
    ):
        self.job_id = job_id
        self.engine_type = engine_type
        self.prompt = prompt
        self.settings = settings
        self.output_path = output_path
        self.status = RenderStatus.PENDING
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.result = None


class RenderEngine(ABC):
    """Abstract base class for all render engines."""

    def __init__(self, name: str, supported_formats: List[str]):
        self.name = name
        self.supported_formats = supported_formats
        self.is_available = False
        self.version = None

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the render engine. Return True if successful."""
        pass

    @abstractmethod
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate that the settings are compatible with this engine."""
        pass

    @abstractmethod
    def create_scene(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Create a scene file or configuration based on the prompt and settings."""
        pass

    @abstractmethod
    def render_video(
        self, scene_path: str, output_path: str, progress_callback=None
    ) -> RenderResult:
        """Render the video from the scene. Progress callback should be called with progress updates."""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up temporary files and resources."""
        pass

    def get_supported_resolutions(self) -> List[tuple]:
        """Get list of supported resolutions. Default implementation."""
        return [(1920, 1080), (1280, 720), (3840, 2160)]

    def get_supported_fps(self) -> List[int]:
        """Get list of supported frame rates. Default implementation."""
        return [24, 30, 60]

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the engine."""
        return {
            "name": self.name,
            "available": self.is_available,
            "version": self.version,
            "supported_formats": self.supported_formats,
            "supported_resolutions": self.get_supported_resolutions(),
            "supported_fps": self.get_supported_fps(),
        }


class RenderEngineManager:
    """Manager for all render engines."""

    def __init__(self):
        self.engines: Dict[RenderEngineType, RenderEngine] = {}
        self.active_jobs: Dict[str, RenderJob] = {}
        self.completed_jobs: Dict[str, RenderJob] = {}

    def register_engine(self, engine: RenderEngine) -> None:
        """Register a render engine."""
        self.engines[RenderEngineType(engine.name.lower())] = engine
        logger.info(f"Registered render engine: {engine.name}")

    def get_engine(self, engine_type: RenderEngineType) -> Optional[RenderEngine]:
        """Get a render engine by type."""
        return self.engines.get(engine_type)

    def get_available_engines(self) -> List[RenderEngineType]:
        """Get list of available render engines."""
        available = []
        for engine_type, engine in self.engines.items():
            if engine.is_available:
                available.append(engine_type)
        return available

    def validate_engine_settings(
        self, engine_type: RenderEngineType, settings: Dict[str, Any]
    ) -> bool:
        """Validate settings for a specific engine."""
        engine = self.get_engine(engine_type)
        if engine:
            return engine.validate_settings(settings)
        return False

    def create_render_job(
        self,
        job_id: str,
        engine_type: RenderEngineType,
        prompt: str,
        settings: Dict[str, Any],
        output_path: str,
    ) -> Optional[RenderJob]:
        """Create a new render job."""
        engine = self.get_engine(engine_type)
        if not engine:
            logger.error(f"Engine {engine_type} not found")
            return None

        if not engine.is_available:
            logger.error(f"Engine {engine_type} is not available")
            return None

        if not engine.validate_settings(settings):
            logger.error(f"Invalid settings for engine {engine_type}")
            return None

        job = RenderJob(job_id, engine_type, prompt, settings, output_path)
        self.active_jobs[job_id] = job
        return job

    def update_job_progress(
        self, job_id: str, progress: int, status: RenderStatus = None
    ) -> bool:
        """Update job progress and optionally status."""
        job = self.active_jobs.get(job_id)
        if job:
            job.progress = progress
            if status:
                job.status = status
            return True
        return False

    def complete_job(self, job_id: str, result: RenderResult) -> bool:
        """Mark a job as completed and move it to completed jobs."""
        job = self.active_jobs.pop(job_id, None)
        if job:
            job.result = result
            job.status = (
                RenderStatus.COMPLETED if result.success else RenderStatus.FAILED
            )
            job.end_time = None  # Would be set by actual implementation
            self.completed_jobs[job_id] = job
            logger.info(f"Job {job_id} completed with status: {job.status.value}")
            return True
        return False

    def cancel_job(self, job_id: str) -> bool:
        """Cancel an active job."""
        job = self.active_jobs.get(job_id)
        if job:
            engine = self.get_engine(job.engine_type)
            if engine:
                engine.cleanup()

            job.status = RenderStatus.FAILED
            job.end_time = None  # Would be set by actual implementation
            self.completed_jobs[job_id] = job
            self.active_jobs.pop(job_id, None)
            logger.info(f"Job {job_id} cancelled")
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job."""
        job = self.active_jobs.get(job_id) or self.completed_jobs.get(job_id)
        if job:
            return {
                "job_id": job.job_id,
                "engine_type": job.engine_type.value,
                "status": job.status.value,
                "progress": job.progress,
                "prompt": job.prompt,
                "settings": job.settings,
                "start_time": job.start_time,
                "end_time": job.end_time,
                "result": job.result.__dict__ if job.result else None,
            }
        return None

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all jobs."""
        all_jobs = []
        for job_id in list(self.active_jobs.keys()) + list(self.completed_jobs.keys()):
            job_status = self.get_job_status(job_id)
            if job_status:
                all_jobs.append(job_status)
        return all_jobs

    def cleanup_completed_jobs(self, older_than_hours: int = 24) -> int:
        """Clean up completed jobs older than specified hours."""
        import time
        from datetime import datetime, timedelta

        cutoff_time = time.time() - (older_than_hours * 3600)
        cleaned_count = 0

        completed_jobs_copy = self.completed_jobs.copy()
        for job_id, job in completed_jobs_copy.items():
            # In real implementation, check job.end_time against cutoff_time
            if job.end_time and job.end_time < cutoff_time:
                del self.completed_jobs[job_id]
                cleaned_count += 1

        logger.info(f"Cleaned up {cleaned_count} old completed jobs")
        return cleaned_count


# Global render engine manager instance
render_manager = RenderEngineManager()
