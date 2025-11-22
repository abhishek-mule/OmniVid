#!/usr/bin/env python3
"""
Production video rendering using Blender supervisor and FFmpeg with process isolation.
Integrates all production-grade components for reliable CI deployments.
"""

import asyncio
import os
import subprocess
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Callable, Optional

from .structured_logger import StructuredLogger
from .debounced_writer import debounced_writer


class ProductionRenderer:
    """Production-grade video renderer using Blender + FFmpeg with process isolation."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.logger = StructuredLogger(job_id, log_file=None)  # Could be made configurable
        self.temp_dir = None

    async def render_video_production(
        self,
        prompt: str,
        settings: Dict[str, Any],
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Render video using production infrastructure with full error recovery.

        Args:
            prompt: Text description of what to render
            settings: Render settings (resolution, fps, duration, etc.)
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with render results and metrics
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Phase 1: Initialize job workspace
            self.logger.info("Initializing production render workspace")
            if progress_callback:
                progress_callback(1.0, "Initializing workspace")

            job_dir = Path("data/jobs") / self.job_id
            self.temp_dir = job_dir / "temp"
            blend_dir = job_dir / "blend"
            frames_dir = job_dir / "frames"
            output_dir = job_dir / "output"

            # Ensure directories exist
            for dir_path in [job_dir, self.temp_dir, blend_dir, frames_dir, output_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)

            # Phase 2: Create scene with process isolation
            scene_result = await self._create_scene_production(
                prompt, settings, blend_dir, progress_callback
            )

            if not scene_result["success"]:
                raise RuntimeError(f"Scene creation failed: {scene_result['error']}")

            blend_path = scene_result["blend_path"]

            # Phase 3: Render frames with atomic operations
            frames_result = await self._render_frames_production(
                blend_path, settings, frames_dir, progress_callback
            )

            if not frames_result["success"]:
                raise RuntimeError(f"Frame rendering failed: {frames_result['error']}")

            # Phase 4: Assemble video
            video_result = await self._assemble_video_production(
                frames_dir, output_dir, settings, progress_callback
            )

            if not video_result["success"]:
                raise RuntimeError(f"Video assembly failed: {video_result['error']}")

            # Phase 5: Final cleanup
            if progress_callback:
                progress_callback(98.0, "Performing final cleanup")

            cleanup_stats = await self._cleanup_production(frames_dir, job_dir)

            # Calculate final metrics
            end_time = asyncio.get_event_loop().time()
            total_duration = end_time - start_time

            result = {
                "success": True,
                "video_url": video_result["video_url"],
                "blend_path": str(blend_path),
                "frames_rendered": frames_result["frames_rendered"],
                "duration_seconds": video_result.get("duration", settings.get("duration", 10)),
                "resolution": settings.get("resolution", [1920, 1080]),
                "output_size_bytes": video_result.get("output_size", 0),
                "metrics": {
                    "total_duration_seconds": total_duration,
                    "scene_creation_time": scene_result.get("duration", 0),
                    "frame_rendering_time": frames_result.get("duration", 0),
                    "assembly_time": video_result.get("duration", 0),
                    "cleanup_stats": cleanup_stats
                }
            }

            if progress_callback:
                progress_callback(100.0, "Render completed successfully")

            self.logger.job_complete(total_duration, True, frames_result["frames_rendered"])
            return result

        except Exception as e:
            error_duration = asyncio.get_event_loop().time() - start_time
            error_msg = f"Production render failed: {str(e)}"
            self.logger.error(error_msg, {"traceback": traceback.format_exc()})

            if progress_callback:
                progress_callback(0.0, "Render failed")

            # Attempt cleanup even on failure
            try:
                if self.temp_dir and self.temp_dir.exists():
                    cleanup_stats = await self._cleanup_production(self.temp_dir.parent / "frames", self.temp_dir.parent)
                    self.logger.info(f"Cleanup completed after failure: {cleanup_stats}")
            except Exception as cleanup_error:
                self.logger.warning(f"Cleanup failed after error: {cleanup_error}")

            self.logger.job_complete(error_duration, False, 0)
            return {
                "success": False,
                "error": error_msg,
                "duration_seconds": error_duration,
                "metrics": {"error_duration": error_duration}
            }

    async def _create_scene_production(
        self, prompt: str, settings: Dict[str, Any], blend_dir: Path,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Create Blender scene using process isolation."""
        scene_start = asyncio.get_event_loop().time()

        try:
            if progress_callback:
                progress_callback(5.0, "Starting scene creation")

            self.logger.info("Starting scene creation in isolated process", {
                "prompt_length": len(prompt),
                "settings": settings
            })

            # Import here to avoid circular imports
            from ..render_engines.blender.engine import BlenderRenderEngine

            engine = BlenderRenderEngine()
            if not engine.initialize():
                raise RuntimeError("Failed to initialize Blender engine")

            # Create blend file in isolated process
            blend_path = engine.create_scene(prompt, settings)
            if not blend_path or not Path(blend_path).exists():
                raise RuntimeError("Scene creation did not produce valid .blend file")

            duration = asyncio.get_event_loop().time() - scene_start

            if progress_callback:
                progress_callback(15.0, "Scene created successfully")

            self.logger.phase_complete("scene_creation", duration, True)
            return {
                "success": True,
                "blend_path": Path(blend_path),
                "duration": duration
            }

        except Exception as e:
            duration = asyncio.get_event_loop().time() - scene_start
            error_msg = f"Scene creation failed: {str(e)}"
            self.logger.phase_complete("scene_creation", duration, False)
            return {
                "success": False,
                "error": error_msg,
                "duration": duration
            }

    async def _render_frames_production(
        self, blend_path: Path, settings: Dict[str, Any], frames_dir: Path,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Render frames using production pipeline with atomic operations."""
        render_start = asyncio.get_event_loop().time()

        try:
            self.logger.info("Starting frame rendering with atomic operations", {
                "blend_path": str(blend_path),
                "frames_dir": str(frames_dir),
                "resolution": settings.get("resolution"),
                "fps": settings.get("fps"),
                "duration": settings.get("duration")
            })

            if progress_callback:
                progress_callback(20.0, "Preprocessing frames")

            # Use existing production frame renderer
            from ..render_engines.blender.templates.render_frames_production import (
                render_frame_range_production
            )

            # Create progress callback for frame renderer
            def frame_progress(progress: float, status: str, message: str):
                # Translate progress (main render = 20-85% of total job)
                job_progress = 20.0 + (progress * 0.65)
                if progress_callback:
                    progress_callback(job_progress, message)

                self.logger.frame_progress(
                    int(progress * settings.get("duration", 10) * settings.get("fps", 30) / 100),
                    int(settings.get("duration", 10) * settings.get("fps", 30))
                )

            # Execute rendering
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                render_frame_range_production,
                blend_path,
                None,  # manifest_path (we could create one)
                frames_dir,
                1,  # start_frame
                int(settings.get("duration", 10) * settings.get("fps", 30)),  # end_frame
                frame_progress
            )

            duration = asyncio.get_event_loop().time() - render_start

            if result["success"]:
                frames_rendered = result["frames_rendered"]

                if progress_callback:
                    progress_callback(85.0, f"Rendered {frames_rendered} frames successfully")

                self.logger.phase_complete("frame_rendering", duration, True)
                return {
                    "success": True,
                    "frames_rendered": frames_rendered,
                    "duration": duration
                }
            else:
                error_details = "; ".join(result.get("errors", ["Unknown error"]))
                self.logger.phase_complete("frame_rendering", duration, False)
                return {
                    "success": False,
                    "error": f"Frame rendering failed: {error_details}",
                    "duration": duration
                }

        except Exception as e:
            duration = asyncio.get_event_loop().time() - render_start
            error_msg = f"Frame rendering exception: {str(e)}"
            self.logger.phase_complete("frame_rendering", duration, False)
            return {
                "success": False,
                "error": error_msg,
                "duration": duration
            }

    async def _assemble_video_production(
        self, frames_dir: Path, output_dir: Path, settings: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Assemble video from rendered frames using FFmpeg supervisor."""
        assembly_start = asyncio.get_event_loop().time()

        try:
            if progress_callback:
                progress_callback(88.0, "Starting video assembly")

            self.logger.info("Starting video assembly with FFmpeg supervisor", {
                "frames_dir": str(frames_dir),
                "output_dir": str(output_dir),
                "fps": settings.get("fps", 30)
            })

            video_filename = f"{self.job_id}.mp4"
            video_path = output_dir / video_filename

            # Use production video assembly
            from ..render_engines.blender.templates.render_frames_production import assemble_video_production

            # Create progress callback for assembly
            def assembly_progress(progress: float, status: str, message: str):
                job_progress = 88.0 + (progress - 88.0) * 0.1  # Assembly = 88-98%
                if progress_callback:
                    progress_callback(job_progress, message)

            success = await asyncio.get_event_loop().run_in_executor(
                None,
                assemble_video_production,
                frames_dir,
                video_path,
                settings.get("fps", 30),
                assembly_progress
            )

            duration = asyncio.get_event_loop().time() - assembly_start

            if success:
                output_size = video_path.stat().st_size if video_path.exists() else 0

                if progress_callback:
                    progress_callback(98.0, "Video assembly completed")

                self.logger.phase_complete("video_assembly", duration, True)
                self.logger.resource_usage("video_assembly", output_size, duration)

                return {
                    "success": True,
                    "video_url": str(video_path),
                    "output_size": output_size,
                    "duration": duration
                }
            else:
                self.logger.phase_complete("video_assembly", duration, False)
                return {
                    "success": False,
                    "error": "FFmpeg video assembly failed",
                    "duration": duration
                }

        except Exception as e:
            duration = asyncio.get_event_loop().time() - assembly_start
            error_msg = f"Video assembly exception: {str(e)}"
            self.logger.phase_complete("video_assembly", duration, False)
            return {
                "success": False,
                "error": error_msg,
                "duration": duration
            }

    async def _cleanup_production(self, frames_dir: Path, job_dir: Path) -> Dict[str, int]:
        """Perform production cleanup with detailed statistics."""
        try:
            # Use the improved cleanup function with statistics
            from ..render_engines.blender.templates.render_frames_production import cleanup_temp_frames

            stats = cleanup_temp_frames(frames_dir, max_age_hours=1)  # Dict return type

            self.logger.info("Cleanup completed", {
                "bytes_freed": stats.get("bytes_freed", 0),
                "files_cleaned": stats.get("files_cleaned", 0),
                "dirs_removed": stats.get("dirs_removed", 0)
            })

            return dict(stats)  # Ensure we return a dict

        except Exception as e:
            self.logger.warning(f"Cleanup error: {str(e)}")
            return {"bytes_freed": 0, "files_cleaned": 0, "dirs_removed": 0}


async def render_video_production_async(
    job_id: str,
    prompt: str,
    settings: Dict[str, Any],
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    Render video using production infrastructure asynchronously.

    This is the main entry point for production video rendering.
    """
    renderer = ProductionRenderer(job_id)

    try:
        result = await renderer.render_video_production(prompt, settings, progress_callback)

        # Flush any pending debounced writes
        await debounced_writer.flush_all()

        return result

    except Exception as e:
        error_msg = f"Critical production render error: {str(e)}"
        renderer.logger.error(error_msg, {"traceback": traceback.format_exc()})

        # Flush logs even on error
        await debounced_writer.flush_all()

        return {
            "success": False,
            "error": error_msg,
            "critical_failure": True
        }
