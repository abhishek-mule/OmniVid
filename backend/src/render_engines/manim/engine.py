"""
Manim render engine implementation.
"""

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from .base import RenderEngine, RenderEngineType, RenderResult, RenderStatus

logger = logging.getLogger(__name__)


class ManimRenderEngine(RenderEngine):
    """Manim render engine for mathematical animations."""

    def __init__(self):
        super().__init__("Manim", ["mp4", "webm"])
        self.manim_path = None
        self.temp_dir = None

    def initialize(self) -> bool:
        """Initialize Manim and check if it's available."""
        try:
            # Check if manim is available
            import shutil

            self.manim_path = shutil.which("manim")

            if not self.manim_path:
                # Check pip installed manim
                result = subprocess.run(
                    ["python", "-m", "manim", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    self.manim_path = "python -m manim"

            if self.manim_path:
                # Get Manim version
                result = subprocess.run(
                    self.manim_path.split() + ["--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    self.version = result.stdout.strip()
                    self.is_available = True
                    logger.info(f"Manim initialized successfully: {self.version}")
                    return True

            logger.warning("Manim not found or not accessible")
            return False

        except Exception as e:
            logger.error(f"Failed to initialize Manim: {str(e)}")
            return False

    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate Manim-specific settings."""
        try:
            # Manim is simpler, basic validation
            resolution = settings.get("resolution", (1920, 1080))
            if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
                return False

            return True

        except Exception:
            return False

    def create_scene(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Create a Manim scene from prompt."""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="omnivid_manim_")

            # Generate Manim Python code
            manim_code = self._generate_manim_code(prompt, settings)

            # Save Python file
            python_file = os.path.join(self.temp_dir, "scene.py")
            with open(python_file, "w") as f:
                f.write(manim_code)

            return python_file

        except Exception as e:
            logger.error(f"Error creating Manim scene: {str(e)}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise

    def render_video(
        self, scene_path: str, output_path: str, progress_callback=None
    ) -> RenderResult:
        """Render video using Manim."""
        try:
            if progress_callback:
                progress_callback(0, RenderStatus.INITIALIZING, "Starting Manim render")

            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if progress_callback:
                progress_callback(20, RenderStatus.RENDERING, "Compiling Manim scene")

            # Run Manim render
            cmd = self.manim_path.split() + [
                "-ql",  # Quality level (l = low, m = medium, h = high)
                scene_path,
                "Scene",  # Class name in the generated code
            ]

            if progress_callback:
                progress_callback(30, RenderStatus.RENDERING, "Rendering animations")

            result = subprocess.run(
                cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                if progress_callback:
                    progress_callback(90, RenderStatus.POST_PROCESSING, "Finalizing")

                # Find generated video file
                media_dir = os.path.join(self.temp_dir, "media", "videos", "720p30")
                video_file = os.path.join(media_dir, "Scene.mp4")

                if os.path.exists(video_file):
                    shutil.copy2(video_file, output_path)

                    if progress_callback:
                        progress_callback(
                            100, RenderStatus.COMPLETED, "Render completed"
                        )

                    return RenderResult(
                        success=True,
                        video_url=output_path,
                        duration=10.0,  # Manim defaults
                        resolution=settings.get("resolution", (1920, 1080)),
                        metadata={
                            "render_engine": "manim",
                            "manim_version": self.version,
                        },
                    )
                else:
                    raise RuntimeError("Manim output file not found")
            else:
                error_msg = f"Manim render failed: {result.stderr}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(0, RenderStatus.FAILED, error_msg)

                return RenderResult(
                    success=False,
                    error_message=error_msg,
                    metadata={"stderr": result.stderr},
                )

        except Exception as e:
            error_msg = f"Manim render error: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(0, RenderStatus.FAILED, error_msg)
            return RenderResult(success=False, error_message=error_msg)

        finally:
            self.cleanup()

    def cleanup(self) -> bool:
        """Clean up temporary files."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup Manim temp files: {str(e)}")
            return False

    def _generate_manim_code(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Generate Manim Python code from prompt."""
        # Simple prompt parsing for mathematical content
        math_keywords = ["equation", "graph", "function", "formula", "math", "geometry"]
        has_math = any(keyword in prompt.lower() for keyword in math_keywords)

        code = f"""
from manim import *

class Scene(Scene):
    def construct(self):
        # Manim scene for: {prompt}
        {'# Mathematical content detected' if has_math else '# General animation'}
        
        # Create title
        title = Text("{prompt}")
        title.scale(1.5)
        title.to_edge(UP)
        
        # Add content based on prompt
        if "circle" in "{prompt}".lower():
            circle = Circle()
            circle.set_fill(PINK, opacity=0.5)
            self.play(Create(circle))
        
        elif "square" in "{prompt}".lower():
            square = Square()
            square.set_fill(BLUE, opacity=0.5)
            self.play(Create(square))
        
        else:
            # Default content
            default = Text("OmniVid Render")
            default.scale(2)
            self.play(Write(default))
        
        self.wait(2)
"""
        return code

    def get_supported_resolutions(self) -> List[tuple]:
        """Get Manim-supported resolutions."""
        return [(854, 480), (1280, 720), (1920, 1080)]

    def get_supported_fps(self) -> List[int]:
        """Get Manim-supported frame rates."""
        return [15, 30, 60]
