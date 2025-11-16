"""
Render pipeline service for coordinating video render engines.
"""
import os
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import logging

from ..render_engines.base import RenderEngineManager, RenderEngineType, RenderStatus, RenderResult
from ..render_engines.blender.engine import BlenderRenderEngine
from ..render_engines.ffmpeg.engine import FfmpegRenderEngine
from ..render_engines.manim.engine import ManimRenderEngine
from ..render_engines.remotion.engine import RemotionRenderEngine

logger = logging.getLogger(__name__)

class RenderPipelineService:
    """Service for managing video rendering across multiple engines."""
    
    def __init__(self):
        self.render_manager = RenderEngineManager()
        self.initialize_engines()
        self.active_renders = {}
    
    def initialize_engines(self):
        """Initialize all available render engines."""
        # Create and register engines
        engines = [
            BlenderRenderEngine(),
            FfmpegRenderEngine(),
            ManimRenderEngine(),
            RemotionRenderEngine()
        ]
        
        for engine in engines:
            try:
                if engine.initialize():
                    self.render_manager.register_engine(engine)
                    logger.info(f"Registered {engine.name} render engine")
                else:
                    logger.warning(f"Failed to initialize {engine.name} engine")
            except Exception as e:
                logger.error(f"Error initializing {engine.name}: {str(e)}")
    
    def get_available_engines(self) -> List[Dict[str, Any]]:
        """Get information about available render engines."""
        available_types = self.render_manager.get_available_engines()
        engines_info = []
        
        for engine_type in available_types:
            engine = self.render_manager.get_engine(engine_type)
            if engine:
                engines_info.append(engine.get_engine_info())
        
        return engines_info
    
    def suggest_engine(self, prompt: str, settings: Dict[str, Any]) -> RenderEngineType:
        """Suggest the best render engine based on prompt and settings."""
        prompt_lower = prompt.lower()
        
        # Mathematical content - suggest Manim
        math_keywords = ["equation", "graph", "function", "formula", "mathematics", "geometry", "calculus"]
        if any(keyword in prompt_lower for keyword in math_keywords):
            return RenderEngineType.MANIM
        
        # 3D content - suggest Blender
        three_d_keywords = ["3d", "cube", "sphere", "cylinder", "animation", "rotate", "transform"]
        if any(keyword in prompt_lower for keyword in three_d_keywords):
            return RenderEngineType.BLENDER
        
        # React/web content - suggest Remotion
        web_keywords = ["react", "component", "web", "html", "ui", "interface"]
        if any(keyword in prompt_lower for keyword in web_keywords):
            return RenderEngineType.REMOTION
        
        # Default to FFmpeg for general video processing
        return RenderEngineType.FFMPEG
    
    def start_render(
        self,
        prompt: str,
        settings: Dict[str, Any],
        output_path: str,
        engine_type: Optional[RenderEngineType] = None,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Start a video render job."""
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Auto-suggest engine if not specified
            if engine_type is None:
                engine_type = self.suggest_engine(prompt, settings)
            
            # Validate engine availability
            if engine_type not in self.render_manager.get_available_engines():
                raise ValueError(f"Engine {engine_type} is not available")
            
            # Validate settings for selected engine
            if not self.render_manager.validate_engine_settings(engine_type, settings):
                raise ValueError(f"Invalid settings for engine {engine_type}")
            
            # Create render job
            job = self.render_manager.create_render_job(
                job_id, engine_type, prompt, settings, output_path
            )
            
            if not job:
                raise RuntimeError(f"Failed to create render job for engine {engine_type}")
            
            # Store job with progress callback
            self.active_renders[job_id] = {
                "job": job,
                "progress_callback": progress_callback,
                "start_time": datetime.now()
            }
            
            # Start rendering in background thread
            self._execute_render_job(job_id, job)
            
            logger.info(f"Started render job {job_id} with engine {engine_type.value}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to start render job: {str(e)}")
            raise
    
    def get_render_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a render job."""
        return self.render_manager.get_job_status(job_id)
    
    def cancel_render(self, job_id: str) -> bool:
        """Cancel a render job."""
        try:
            if self.render_manager.cancel_job(job_id):
                self.active_renders.pop(job_id, None)
                logger.info(f"Cancelled render job {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel render job {job_id}: {str(e)}")
            return False
    
    def get_all_render_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all render jobs."""
        return self.render_manager.get_all_jobs()
    
    def get_render_statistics(self) -> Dict[str, Any]:
        """Get render pipeline statistics."""
        active_count = len(self.active_renders)
        total_jobs = len(self.render_manager.completed_jobs) + active_count
        
        engine_usage = {}
        for job in self.render_manager.completed_jobs.values():
            engine = job.engine_type.value
            engine_usage[engine] = engine_usage.get(engine, 0) + 1
        
        return {
            "active_renders": active_count,
            "total_completed": len(self.render_manager.completed_jobs),
            "total_jobs": total_jobs,
            "available_engines": len(self.render_manager.get_available_engines()),
            "engine_usage": engine_usage,
            "engines": self.get_available_engines()
        }
    
    def cleanup_old_jobs(self, older_than_hours: int = 24) -> int:
        """Clean up old completed render jobs."""
        return self.render_manager.cleanup_completed_jobs(older_than_hours)
    
    def _execute_render_job(self, job_id: str, job):
        """Execute a render job in a background thread."""
        def render_worker():
            try:
                engine = self.render_manager.get_engine(job.engine_type)
                if not engine:
                    raise RuntimeError(f"Engine {job.engine_type} not found")
                
                # Create progress callback
                def progress_callback(progress, status, message):
                    self.render_manager.update_job_progress(job_id, progress, status)
                    if job_id in self.active_renders:
                        callback = self.active_renders[job_id]["progress_callback"]
                        if callback:
                            callback(progress, status, message)
                
                # Update job status
                job.status = RenderStatus.INITIALIZING
                job.start_time = datetime.now()
                
                # Create scene
                scene_path = engine.create_scene(job.prompt, job.settings)
                
                # Render video
                result = engine.render_video(scene_path, job.output_path, progress_callback)
                
                # Complete job
                self.render_manager.complete_job(job_id, result)
                
            except Exception as e:
                logger.error(f"Render job {job_id} failed: {str(e)}")
                error_result = RenderResult(
                    success=False,
                    error_message=str(e)
                )
                self.render_manager.complete_job(job_id, error_result)
            
            finally:
                # Remove from active renders
                self.active_renders.pop(job_id, None)
        
        # Start worker thread
        import threading
        worker_thread = threading.Thread(target=render_worker, daemon=True)
        worker_thread.start()

# Global render pipeline service instance
render_pipeline = RenderPipelineService()