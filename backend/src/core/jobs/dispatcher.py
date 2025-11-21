"""
Job Dispatcher: Submits rendering tasks to the processing queue.
"""
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class Job:
    """Represents a video generation job."""

    def __init__(
        self,
        job_id: str,
        prompt: str,
        scene_json: Dict[str, Any],
        output_path: str,
        priority: int = 1
    ):
        self.job_id = job_id
        self.prompt = prompt
        self.scene_json = scene_json
        self.output_path = output_path
        self.priority = priority
        self.status = "pending"
        self.progress = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.worker_id = None
        self.result = None
        self.error = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "prompt": self.prompt,
            "scene_json": self.scene_json,
            "output_path": self.output_path,
            "priority": self.priority,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "worker_id": self.worker_id,
            "result": self.result,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        job = cls(
            job_id=data["job_id"],
            prompt=data["prompt"],
            scene_json=data["scene_json"],
            output_path=data["output_path"],
            priority=data.get("priority", 1)
        )
        job.status = data.get("status", "pending")
        job.progress = data.get("progress", 0)
        job.worker_id = data.get("worker_id")
        job.result = data.get("result")
        job.error = data.get("error")
        return job

class JobDispatcher:
    """Manages the job queue and dispatches tasks to workers."""

    def __init__(self):
        # In-memory job storage (in production, use Redis or database)
        self.jobs: Dict[str, Job] = {}
        self.workers: Dict[str, Dict[str, Any]] = {}
        # Callback for when job status changes
        self.status_callbacks: List[Callable[[Job], None]] = []

    def submit_job(
        self,
        prompt: str,
        scene_json: Dict[str, Any],
        output_path: str,
        priority: int = 1
    ) -> str:
        """
        Submit a new rendering job.

        Args:
            prompt: Original natural language prompt
            scene_json: Parsed scene data
            output_path: Where to save final video
            priority: Job priority (higher = more urgent)

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, prompt, scene_json, output_path, priority)

        self.jobs[job_id] = job
        logger.info(f"Submitted job {job_id} with priority {priority}")

        # Auto-assign to available worker
        self._assign_job_to_worker(job)

        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        job = self.jobs.get(job_id)
        if job:
            return job.to_dict()
        return None

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all jobs."""
        return [job.to_dict() for job in self.jobs.values()]

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if it's not already completed."""
        job = self.jobs.get(job_id)
        if job and job.status in ["pending", "running"]:
            job.status = "cancelled"
            self._notify_status_change(job)
            logger.info(f"Cancelled job {job_id}")
            return True
        return False

    def register_worker(self, worker_id: str, capabilities: List[str]) -> None:
        """Register a worker with its capabilities."""
        self.workers[worker_id] = {
            "worker_id": worker_id,
            "capabilities": capabilities,  # ["remotion", "manim", "ffmpeg"]
            "active_jobs": [],
            "last_seen": datetime.now()
        }
        logger.info(f"Registered worker {worker_id} with capabilities: {capabilities}")

        # Try to assign pending jobs to new worker
        self._assign_pending_jobs()

    def unregister_worker(self, worker_id: str) -> None:
        """Unregister a worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            logger.info(f"Unregistered worker {worker_id}")

    def worker_heartbeat(self, worker_id: str, job_statuses: List[Dict[str, Any]]) -> None:
        """Handle heartbeat from worker with job status updates."""
        if worker_id in self.workers:
            self.workers[worker_id]["last_seen"] = datetime.now()

            # Update job statuses
            for status_update in job_statuses:
                job_id = status_update.get("job_id")
                status = status_update.get("status")
                progress = status_update.get("progress", 0)
                result = status_update.get("result")
                error = status_update.get("error")

                job = self.jobs.get(job_id)
                if job:
                    job.status = status
                    job.progress = progress

                    if status == "running" and not job.started_at:
                        job.started_at = datetime.now()
                        job.worker_id = worker_id

                    if status in ["completed", "failed"]:
                        job.completed_at = datetime.now()
                        job.result = result
                        job.error = error

                        # Remove from worker's active jobs
                        if worker_id in self.workers:
                            active_jobs = self.workers[worker_id]["active_jobs"]
                            if job_id in active_jobs:
                                active_jobs.remove(job_id)

                    self._notify_status_change(job)

    def get_pending_jobs(self) -> List[Job]:
        """Get all pending jobs sorted by priority."""
        pending = [job for job in self.jobs.values() if job.status == "pending"]
        return sorted(pending, key=lambda j: j.priority, reverse=True)

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics about workers and jobs."""
        return {
            "total_workers": len(self.workers),
            "total_jobs": len(self.jobs),
            "pending_jobs": len([j for j in self.jobs.values() if j.status == "pending"]),
            "running_jobs": len([j for j in self.jobs.values() if j.status == "running"]),
            "completed_jobs": len([j for j in self.jobs.values() if j.status == "completed"]),
            "failed_jobs": len([j for j in self.jobs.values() if j.status == "failed"])
        }

    def add_status_callback(self, callback: Callable[[Job], None]) -> None:
        """Add callback to be called when job status changes."""
        self.status_callbacks.append(callback)

    def _notify_status_change(self, job: Job) -> None:
        """Notify all callbacks about job status change."""
        for callback in self.status_callbacks:
            try:
                callback(job)
            except Exception as e:
                logger.error(f"Status callback failed: {e}")

    def _assign_job_to_worker(self, job: Job) -> None:
        """Try to assign job to an available worker."""
        required_engine = self._get_required_engine(job.scene_json)

        for worker_id, worker_info in self.workers.items():
            capabilities = worker_info["capabilities"]
            active_jobs = worker_info["active_jobs"]

            # Check if worker can handle this job and isn't overloaded
            if required_engine in capabilities and len(active_jobs) < 3:  # Max 3 jobs per worker
                active_jobs.append(job.job_id)
                job.status = "assigned"
                job.worker_id = worker_id
                logger.info(f"Assigned job {job.job_id} to worker {worker_id}")

                # Simulate immediate start (in real implementation, worker would pull)
                job.status = "running"
                job.started_at = datetime.now()
                self._notify_status_change(job)
                break

    def _assign_pending_jobs(self) -> None:
        """Assign pending jobs to available workers."""
        pending_jobs = self.get_pending_jobs()
        for job in pending_jobs:
            self._assign_job_to_worker(job)

    def _get_required_engine(self, scene_json: Dict[str, Any]) -> str:
        """Get the primary engine required for scene JSON."""
        timeline = scene_json.get("timeline", [])
        if not timeline:
            return "remotion"  # Default

        first_scene = timeline[0]
        engine = first_scene.get("engine", "remotion")

        # Validate engine
        valid_engines = ["remotion", "manim", "blender", "ffmpeg"]
        return engine if engine in valid_engines else "remotion"

    def cleanup_old_jobs(self, days: int = 7) -> int:
        """Remove jobs older than specified days."""
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Simple implementation - in practice would check timestamps
        return 0

# Global instance
job_dispatcher = JobDispatcher()
