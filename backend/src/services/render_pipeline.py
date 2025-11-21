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
from .ai_service import ai_service

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
    
    async def start_ai_render(
        self,
        prompt: str,
        output_path: str,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """Start an AI-driven video render from natural language prompt."""
        try:
            # Generate unique job ID
            job_id = str(uuid.uuid4())

            logger.info(f"Processing AI prompt: {prompt[:50]}...")

            # Process prompt through AI service
            ai_spec = await ai_service.process_prompt(prompt)

            # Extract engine and settings from AI specification
            code_spec = ai_spec['code_spec']

            # Map string engine name to RenderEngineType enum
            engine_name_mapping = {
                'remotion': RenderEngineType.REMOTION,
                'manim': RenderEngineType.MANIM,
                'blender': RenderEngineType.BLENDER,
                'ffmpeg': RenderEngineType.FFMPEG
            }

            engine_type = engine_name_mapping.get(code_spec['engine'])
            if not engine_type:
                raise ValueError(f"Unsupported engine: {code_spec['engine']}")

            # Validate engine availability
            if engine_type not in self.render_manager.get_available_engines():
                raise ValueError(f"Engine {engine_type} is not available")

            # Combine AI-extracted settings with code spec config
            render_settings = {
                **ai_spec['parameters'],
                'code': code_spec['code'],
                'config': code_spec['config'],
                'ai_spec': ai_spec  # Store full AI specification for reference
            }

            # Validate settings for selected engine
            if not self.render_manager.validate_engine_settings(engine_type, render_settings):
                raise ValueError(f"Invalid settings for engine {engine_type}")

            # Create render job
            job = self.render_manager.create_render_job(
                job_id, engine_type, prompt, render_settings, output_path
            )

            if not job:
                raise RuntimeError(f"Failed to create AI render job for engine {engine_type}")

            # Store job with AI context and progress callback
            self.active_renders[job_id] = {
                "job": job,
                "ai_spec": ai_spec,
                "progress_callback": progress_callback,
                "start_time": datetime.now()
            }

            # Start rendering in background thread
            self._execute_ai_render_job(job_id, job, ai_spec)

            logger.info(f"Started AI render job {job_id} with engine {engine_type.value} for scene: {ai_spec['scene_type']}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to start AI render job: {str(e)}")
            raise

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

    def _execute_ai_render_job(self, job_id: str, job, ai_spec: Dict[str, Any]):
        """Execute an AI-driven render job with the compiler-style pipeline."""
        def ai_render_worker():
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

                # Step 1: Generate and write code for the engine
                progress_callback(10, RenderStatus.INITIALIZING, "Generating animation code...")

                code_spec = ai_spec['code_spec']
                code_content = code_spec['code']
                config = code_spec.get('config', {})

                # Create temporary scene file with generated code
                scene_path = self._create_scene_from_code(code_spec, job_id)

                # Step 2: Execute the engine render
                progress_callback(30, RenderStatus.RENDERING, f"Rendering with {job.engine_type.value}...")

                # Pass the code and config via job settings
                render_settings = {
                    **job.settings,
                    'generated_code': code_content,
                    'scene_config': config
                }

                # Use the engine to create and render the scene
                final_result = engine.render_video(scene_path, job.output_path, progress_callback)

                if not final_result.success:
                    raise RuntimeError(f"Engine render failed: {final_result.error_message}")

                # Step 3: Post-processing with FFmpeg (if needed)
                pipeline = ai_spec.get('pipeline', [])
                if len(pipeline) > 1:  # More than just the render step
                    progress_callback(80, RenderStatus.POST_PROCESSING, "Post-processing video...")

                    # Find FFmpeg post-processing step
                    ffmpeg_step = None
                    for step in pipeline[1:]:  # Skip the first render step
                        if step.get('engine') == 'ffmpeg':
                            ffmpeg_step = step
                            break

                    if ffmpeg_step:
                        final_result = self._apply_ffmpeg_post_processing(
                            job.output_path, ffmpeg_step, final_result
                        )

                # Step 4: Final cleanup and completion
                progress_callback(95, RenderStatus.POST_PROCESSING, "Finalizing...")

                # Complete job
                self.render_manager.complete_job(job_id, final_result)

                progress_callback(100, RenderStatus.COMPLETED, "AI video generation completed!")

            except Exception as e:
                logger.error(f"AI render job {job_id} failed: {str(e)}")
                error_result = RenderResult(
                    success=False,
                    error_message=f"AI video generation failed: {str(e)}"
                )
                self.render_manager.complete_job(job_id, error_result)

            finally:
                # Clean up temporary files
                self._cleanup_ai_job_files(job_id)

                # Remove from active renders
                self.active_renders.pop(job_id, None)

        # Start worker thread
        import threading
        worker_thread = threading.Thread(target=ai_render_worker, daemon=True)
        worker_thread.start()

    def _create_scene_from_code(self, code_spec: Dict[str, Any], job_id: str) -> str:
        """Create a scene file from generated code."""
        import tempfile
        import os

        engine = code_spec['engine']
        code_content = code_spec['code']
        config = code_spec.get('config', {})

        # Create temporary directory for this job
        temp_dir = os.path.join(tempfile.gettempdir(), f"omnivid_ai_{job_id}")
        os.makedirs(temp_dir, exist_ok=True)

        if engine == 'remotion':
            # Create Remotion component file
            scene_file = os.path.join(temp_dir, 'Scene.tsx')
            with open(scene_file, 'w', encoding='utf-8') as f:
                f.write(code_content)

            # Create remotion.config.ts if needed
            config_content = f'''import {{ Config }} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setPixelFormat('yuv420p');

Config.setStudioPort(3001);

export default Config;
'''
            config_file = os.path.join(temp_dir, 'remotion.config.ts')
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)

            return scene_file

        elif engine == 'manim':
            # Create Manim Python file
            scene_file = os.path.join(temp_dir, 'scene.py')
            with open(scene_file, 'w', encoding='utf-8') as f:
                f.write(code_content)
            return scene_file

        else:
            # For other engines, create a generic temp file
            scene_file = os.path.join(temp_dir, 'scene.txt')
            with open(scene_file, 'w', encoding='utf-8') as f:
                f.write(code_content)
            return scene_file

    def _apply_ffmpeg_post_processing(
        self,
        input_path: str,
        ffmpeg_step: Dict[str, Any],
        current_result: RenderResult
    ) -> RenderResult:
        """Apply FFmpeg post-processing to the rendered video."""
        try:
            ffmpeg_engine = self.render_manager.get_engine(RenderEngineType.FFMPEG)
            if not ffmpeg_engine:
                logger.warning("FFmpeg engine not available for post-processing")
                return current_result

            operations = ffmpeg_step.get('operations', [])
            output_path = ffmpeg_step.get('output', input_path)

            # For now, just copy if no specific operations
            if not operations or operations == ['optimize', 'compress']:
                # Simple optimization - could be extended
                import shutil
                if input_path != output_path:
                    shutil.copy2(input_path, output_path)
                return RenderResult(
                    success=True,
                    video_url=output_path,
                    duration=current_result.duration,
                    resolution=current_result.resolution
                )

            return current_result

        except Exception as e:
            logger.error(f"FFmpeg post-processing failed: {str(e)}")
            return current_result  # Return original result if post-processing fails

    def _cleanup_ai_job_files(self, job_id: str):
        """Clean up temporary files created during AI job processing."""
        try:
            import tempfile
            import shutil
            import os

            temp_dir = os.path.join(tempfile.gettempdir(), f"omnivid_ai_{job_id}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary AI job files for {job_id}")
        except Exception as e:
            logger.warning(f"Failed to cleanup AI job files for {job_id}: {str(e)}")

# Global render pipeline service instance
render_pipeline = RenderPipelineService()
