"""
FFmpeg render engine implementation.
"""

import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import RenderEngine, RenderEngineType, RenderResult, RenderStatus

logger = logging.getLogger(__name__)


class FFMpegSupervisor:
    """Lightweight supervisor for FFMPEG processes with retry logic."""

    def __init__(self, ffmpeg_path: str):
        self.ffmpeg_path = Path(ffmpeg_path)
        self.ffprobe_path = None
        self._find_ffprobe()

    def _find_ffprobe(self):
        """Find ffprobe executable in same directory as ffmpeg."""
        ffmpeg_dir = self.ffmpeg_path.parent
        ffprobe_path = ffmpeg_dir / "ffprobe"
        if os.name == 'nt':  # Windows
            ffprobe_path = ffmpeg_dir / "ffprobe.exe"

        if ffprobe_path.exists() and os.access(ffprobe_path, os.X_OK):
            self.ffprobe_path = ffprobe_path
        else:
            # Try system PATH
            try:
                import shutil
                ffprobe_sys = shutil.which("ffprobe")
                if ffprobe_sys:
                    self.ffprobe_path = Path(ffprobe_sys)
            except:
                pass

    def has_ffprobe(self) -> bool:
        """Check if ffprobe is available."""
        return self.ffprobe_path is not None and self.ffprobe_path.exists()

    def execute_with_retry(
        self,
        cmd: List[str],
        job_id: str,
        timeout_seconds: int = 300,
        max_retries: int = 2
    ) -> Tuple[bool, str, str, int]:
        """
        Execute FFMPEG command with retry logic and progress monitoring.
        Returns: (success, stdout, stderr, exit_code)
        """
        last_stderr = ""
        last_stdout = ""

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"FFMPEG attempt {attempt + 1}/{max_retries + 1} for job {job_id}")

                # Execute command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=os.environ.copy()
                )

                start_time = time.time()
                stdout_parts = []
                stderr_parts = []

                # Monitor with timeout
                while True:
                    if process.poll() is not None:
                        break

                    if time.time() - start_time > timeout_seconds:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        raise subprocess.TimeoutExpired("FFMPEG timeout", timeout=timeout_seconds)

                    time.sleep(0.1)  # Brief polling interval

                # Get final output
                final_stdout, final_stderr = process.communicate()

                stdout_parts.append(final_stdout)
                stderr_parts.append(final_stderr)

                complete_stdout = ''.join(stdout_parts)
                complete_stderr = ''.join(stderr_parts)

                if process.returncode == 0:
                    return True, complete_stdout, complete_stderr, 0

                logger.warning(f"FFMPEG attempt {attempt + 1} failed with code {process.returncode}")

                # Don't retry if it's the last attempt
                if attempt == max_retries:
                    return False, complete_stdout, complete_stderr, process.returncode or -1

                last_stdout = complete_stdout
                last_stderr = complete_stderr

                # Brief delay before retry
                time.sleep(1)

            except subprocess.TimeoutExpired:
                logger.warning(f"FFMPEG timeout on attempt {attempt + 1}")
                if attempt == max_retries:
                    return False, last_stdout, last_stderr, -2
                time.sleep(2)

            except Exception as e:
                logger.error(f"FFMPEG execution error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    return False, last_stdout, last_stderr, -3
                time.sleep(1)

        return False, last_stdout, last_stderr, -4


class FfmpegRenderEngine(RenderEngine):
    """FFmpeg render engine for video processing and creation."""

    def __init__(self):
        super().__init__("FFmpeg", ["mp4", "avi", "mov", "mkv", "webm", "flv"])
        self.ffmpeg_path = None
        self.supervisor = None
        self.temp_dir = None

    def initialize(self) -> bool:
        """Initialize FFmpeg and check if it's available."""
        try:
            # Check if FFmpeg is available in system PATH
            import shutil

            self.ffmpeg_path = shutil.which("ffmpeg")

                # Check common installation paths
                common_paths = [
                    "/usr/bin/ffmpeg",
                    "/usr/local/bin/ffmpeg",
                    "C:\\ffmpeg\\bin\\ffmpeg.exe",
                    "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
                    
                ]

                for path in common_paths:
                    if os.path.exists(path):
                        self.ffmpeg_path = path
                        break

            if self.ffmpeg_path:
                # Get FFmpeg version
                result = subprocess.run(
                    [self.ffmpeg_path, "-version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    # Extract version from output
                    version_line = result.stdout.split("\n")[0]
                    self.version = version_line
                    self.is_available = True
                    logger.info(f"FFmpeg initialized successfully: {version_line}")
                    return True

            logger.warning("FFmpeg not found or not accessible")
            return False

        except Exception as e:
            logger.error(f"Failed to initialize FFmpeg: {str(e)}")
            return False

    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate FFmpeg-specific settings."""
        try:
            # Check resolution
            resolution = settings.get("resolution", (1920, 1080))
            if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
                return False

            # Check frame rate
            fps = settings.get("fps", 30)
            if not isinstance(fps, (int, float)) or fps <= 0:
                return False

            # Check duration
            duration = settings.get("duration", 10)
            if not isinstance(duration, (int, float)) or duration <= 0:
                return False

            # Check codec
            codec = settings.get("codec", "libx264")
            if codec not in ["libx264", "libx265", "libvpx", "libvorbis"]:
                return False

            # Check bitrate
            bitrate = settings.get("bitrate", 5000)
            if not isinstance(bitrate, (int, float)) or bitrate <= 0:
                return False

            return True

        except Exception as e:
            logger.error(f"FFmpeg settings validation failed: {str(e)}")
            return False

    def create_scene(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Create a scene configuration for FFmpeg."""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="omnivid_ffmpeg_")

            # Create a configuration file
            config = {
                "prompt": prompt,
                "settings": settings,
                "input_files": [],
                "filters": [],
                "output_format": settings.get("output_format", "mp4"),
                "temp_dir": self.temp_dir,
            }

            # Save configuration
            config_path = os.path.join(self.temp_dir, "config.json")
            import json

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            # Generate FFmpeg command based on prompt and settings
            ffmpeg_script = self._generate_ffmpeg_script(prompt, settings, config_path)

            # Save script
            script_path = os.path.join(self.temp_dir, "render_script.txt")
            with open(script_path, "w") as f:
                f.write(ffmpeg_script)

            return config_path

        except Exception as e:
            logger.error(f"Error creating FFmpeg scene: {str(e)}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise

    def render_video(
        self, scene_path: str, output_path: str, progress_callback=None
    ) -> RenderResult:
        """Render video using FFmpeg."""
        try:
            if progress_callback:
                progress_callback(
                    0, RenderStatus.INITIALIZING, "Starting FFmpeg render"
                )

            # Load configuration
            import json

            with open(scene_path, "r") as f:
                config = json.load(f)

            settings = config["settings"]

            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if progress_callback:
                progress_callback(20, RenderStatus.RENDERING, "Preparing render")

            # Generate FFmpeg command
            cmd = self._build_ffmpeg_command(settings, output_path)

            if progress_callback:
                progress_callback(30, RenderStatus.RENDERING, "Starting FFmpeg process")

            # Execute FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
            )

            # Monitor progress
            self._monitor_ffmpeg_progress(process, progress_callback)

            # Wait for completion
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                if progress_callback:
                    progress_callback(90, RenderStatus.POST_PROCESSING, "Finalizing")

                # Check if output file exists
                if os.path.exists(output_path):
                    if progress_callback:
                        progress_callback(
                            100, RenderStatus.COMPLETED, "Render completed"
                        )

                    # Get video info
                    duration = self._get_video_duration(output_path)
                    resolution = self._get_video_resolution(output_path)

                    return RenderResult(
                        success=True,
                        video_url=output_path,
                        duration=duration,
                        resolution=resolution,
                        metadata={
                            "render_engine": "ffmpeg",
                            "ffmpeg_version": self.version,
                            "settings": settings,
                            "input_stdin": stdout,
                            "stderr": stderr,
                        },
                    )
                else:
                    raise RuntimeError("Output file was not created")
            else:
                error_msg = f"FFmpeg render failed: {stderr}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(0, RenderStatus.FAILED, error_msg)

                return RenderResult(
                    success=False,
                    error_message=error_msg,
                    metadata={"stderr": stderr, "stdout": stdout},
                )

        except Exception as e:
            error_msg = f"FFmpeg render error: {str(e)}"
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
            logger.error(f"Failed to cleanup FFmpeg temp files: {str(e)}")
            return False

    def _generate_ffmpeg_script(
        self, prompt: str, settings: Dict[str, Any], config_path: str
    ) -> str:
        """Generate FFmpeg command script."""
        script_parts = [
            f"# FFmpeg script for prompt: {prompt}",
            f"# Settings: {settings}",
            "",
            "# Example FFmpeg commands:",
            "ffmpeg -f lavfi -i color=c=blue:s=1920x1080:d=10 -r 30 -c:v libx264 output.mp4",
            "ffmpeg -i input.mp4 -vf scale=1920:1080 -c:v libx264 -preset fast output.mp4",
        ]

        return "\n".join(script_parts)

    def _build_ffmpeg_command(
        self, settings: Dict[str, Any], output_path: str
    ) -> List[str]:
        """Build FFmpeg command based on settings."""
        cmd = [self.ffmpeg_path]

        # Add input (for now, generate a test pattern)
        resolution = settings.get("resolution", (1920, 1080))
        duration = settings.get("duration", 10)
        fps = settings.get("fps", 30)

        # Create a colored background with text as input
        color = "blue"
        cmd.extend(
            [
                "-f",
                "lavfi",
                "-i",
                f"color=c={color}:s={resolution[0]}x{resolution[1]}:d={duration}",
            ]
        )

        # Add filters
        filters = []

        # Add text overlay from prompt
        if "text" in str(settings).lower():
            text = settings.get("text", "FFmpeg Render")
            filters.append(
                f"drawtext=text='{text}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"
            )

        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # Add video codec and settings
        codec = settings.get("codec", "libx264")
        cmd.extend(["-c:v", codec])

        # Add bitrate
        bitrate = settings.get("bitrate", 5000)
        cmd.extend(["-b:v", f"{bitrate}k"])

        # Add framerate
        cmd.extend(["-r", str(fps)])

        # Add output
        cmd.append(output_path)

        return cmd

    def _monitor_ffmpeg_progress(self, process, progress_callback):
        """Monitor FFmpeg process and update progress."""
        if not progress_callback:
            return

        while True:
            output = process.stderr.readline()
            if output == "" and process.poll() is not None:
                break

            if output:
                # Parse FFmpeg output for progress
                if "time=" in output:
                    # Extract time and calculate progress
                    # This is a simplified version - real implementation would be more sophisticated
                    progress_callback(
                        50,  # Default progress
                        RenderStatus.RENDERING,
                        "Processing video frames",
                    )

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using FFprobe."""
        try:
            ffprobe_cmd = [
                self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                video_path,
            ]

            result = subprocess.run(
                ffprobe_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                return float(data["format"]["duration"])

            return 10.0  # Default duration

        except Exception:
            return 10.0

    def _get_video_resolution(self, video_path: str) -> tuple:
        """Get video resolution using FFprobe."""
        try:
            ffprobe_cmd = [
                self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_streams",
                video_path,
            ]

            result = subprocess.run(
                ffprobe_cmd, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                for stream in data["streams"]:
                    if stream["codec_type"] == "video":
                        return (int(stream["width"]), int(stream["height"]))

            return (1920, 1080)  # Default resolution

        except Exception:
            return (1920, 1080)

    def get_supported_resolutions(self) -> List[tuple]:
        """Get FFmpeg-supported resolutions."""
        return [
            (7680, 4320),  # 8K
            (3840, 2160),  # 4K
            (2560, 1440),  # 2K
            (1920, 1080),  # Full HD
            (1280, 720),  # HD
            (854, 480),  # SD
            (640, 360),  # Low
        ]

    def get_supported_fps(self) -> List[int]:
        """Get FFmpeg-supported frame rates."""
        return [15, 23.976, 24, 25, 29.97, 30, 50, 59.94, 60, 120]
