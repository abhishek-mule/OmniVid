"""
Celery Application

Distributed task queue for OMNIVID video rendering jobs.
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import json
from typing import Dict, Any

from config import settings, ensure_directories, get_remotion_root, get_output_path
from remotion_adapter import RemotionAdapter, RenderConfig, RenderResult


# Initialize Celery app
celery_app = Celery(
    "omnivid",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.CELERY_TASK_TRACK_STARTED,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_TIME_LIMIT - 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)


# Task lifecycle hooks
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when task starts."""
    print(f"[TASK START] {task.name} - ID: {task_id}")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **extra):
    """Log when task completes."""
    print(f"[TASK COMPLETE] {task.name} - ID: {task_id}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, **extra):
    """Log when task fails."""
    print(f"[TASK FAILED] {sender.name} - ID: {task_id} - Error: {exception}")


@celery_app.task(name="omnivid.render.remotion", bind=True)
def render_remotion_video(self, render_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to render video using Remotion adapter.
    
    Args:
        render_request: Dictionary containing:
            - remotion_root: Path to Remotion project (optional)
            - composition_id: Composition to render (optional)
            - output_filename: Output filename
            - width: Video width
            - height: Video height
            - fps: Frame rate
            - quality: Quality preset
            - format: Output format
            - codec: Video codec (optional)
            - duration: Video duration (optional)
            - scenes: List of scene configurations (optional)
            - assets: List of asset configurations (optional)
            - additional_params: Additional render parameters (optional)
    
    Returns:
        Dictionary with render result
    """
    try:
        # Update task state
        self.update_state(state="INITIALIZING", meta={"status": "Setting up adapter"})
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize Remotion adapter
        remotion_root = render_request.get("remotion_root") or str(get_remotion_root())
        composition_id = render_request.get("composition_id") or settings.REMOTION_COMPOSITION_ID
        
        adapter = RemotionAdapter(
            remotion_root=remotion_root,
            composition_id=composition_id,
            node_path=settings.NODE_PATH,
            npx_path=settings.NPX_PATH
        )
        
        # Initialize adapter
        if not adapter.initialize():
            return {
                "success": False,
                "error": "Failed to initialize Remotion adapter",
                "task_id": self.request.id
            }
        
        # Update task state
        self.update_state(state="PROCESSING", meta={"status": "Adding assets and scenes"})
        
        # Add assets if provided
        assets = render_request.get("assets", [])
        for asset in assets:
            asset_id = adapter.add_asset(
                asset_path=asset["path"],
                asset_type=asset["type"],
                asset_id=asset.get("id")
            )
            if not asset_id:
                print(f"Warning: Failed to add asset {asset['path']}")
        
        # Add scenes if provided
        scenes = render_request.get("scenes", [])
        for scene in scenes:
            scene_id = adapter.add_scene(scene)
            if not scene_id:
                print(f"Warning: Failed to add scene {scene.get('name', 'unknown')}")
        
        # Prepare render configuration
        output_filename = render_request.get("output_filename", f"video_{self.request.id}.mp4")
        output_path = get_output_path(output_filename)
        
        additional_params = render_request.get("additional_params", {})
        additional_params["timeout"] = settings.RENDER_TIMEOUT
        
        config = RenderConfig(
            output_path=output_path,
            width=render_request.get("width", settings.DEFAULT_WIDTH),
            height=render_request.get("height", settings.DEFAULT_HEIGHT),
            fps=render_request.get("fps", settings.DEFAULT_FPS),
            quality=render_request.get("quality", settings.DEFAULT_QUALITY),
            format=render_request.get("format", settings.DEFAULT_FORMAT),
            codec=render_request.get("codec"),
            duration=render_request.get("duration"),
            additional_params=additional_params
        )
        
        # Update task state
        self.update_state(state="RENDERING", meta={"status": "Rendering video", "output_path": output_path})
        
        # Render video
        result: RenderResult = adapter.render(config)
        
        # Clean up
        adapter.cleanup()
        
        # Prepare response
        return {
            "success": result.status.value == "completed",
            "status": result.status.value,
            "output_path": result.output_path,
            "error": result.error,
            "metadata": result.metadata,
            "task_id": self.request.id
        }
        
    except Exception as e:
        # Log error and return failure
        print(f"Error in render task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "task_id": self.request.id
        }


@celery_app.task(name="omnivid.render.status")
def get_render_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a render task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Task status information
    """
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "state": result.state,
        "status": result.info if isinstance(result.info, dict) else {},
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None
    }


@celery_app.task(name="omnivid.render.cancel")
def cancel_render_task(task_id: str) -> Dict[str, Any]:
    """
    Cancel a render task.
    
    Args:
        task_id: Celery task ID
        
    Returns:
        Cancellation result
    """
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    result.revoke(terminate=True)
    
    return {
        "task_id": task_id,
        "cancelled": True
    }


@celery_app.task(name="omnivid.health.check")
def health_check() -> Dict[str, str]:
    """
    Health check task for monitoring.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "omnivid-celery"}


if __name__ == "__main__":
    # Run worker
    celery_app.start()
