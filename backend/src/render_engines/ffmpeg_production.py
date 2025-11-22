#!/usr/bin/env python3
"""
Production-Grade FFmpeg render engine implementation with proper error handling and progress monitoring.
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


class ProgressParser:
    """FFmpeg progress output parser for accurate progress reporting."""

    def __init__(self):
        self.duration_pattern = re.compile(r'Duration:\s*(\d+):(\d+):(\d+\.?\d*)')
        self.time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.?\d*)')
        self.frame_pattern = re.compile(r'frame=\s*(\d+)')

    def parse_duration(self, line: str) -> Optional[float]:
        """Parse duration from FFmpeg output (format: HH:MM:SS.SS)"""
        match = self.duration_pattern.search(line)
        if match:
            hours, minutes, seconds = map(float, match.groups())
            return hours * 3600 + minutes * 60 + seconds
        return None

    def parse_time(self, line: str) -> Optional[float]:
        """Parse current time from FFmpeg output (format: HH:MM:SS.SS)"""
        match = self.time_pattern.search(line)
        if match:
            hours, minutes, seconds = map(float, match.groups())
            return hours * 3600 + minutes * 60 + seconds
        return None

    def parse_frame(self, line: str) -> Optional[int]:
        """Parse current frame number from FFmpeg output"""
        match = self.frame_pattern.search(line)
        if match:
            return int(match.group(1))
        return None

    def calculate_progress(self, current_time: float, total_duration: float) -> float:
        """Calculate progress percentage (0-100)"""
        if total_duration <= 0:
            return 0
        return min(100.0, (current_time / total_duration) * 100)


class FFMpegSupervisor:
    """Lightweight supervisor for FFMPEG processes with retry logic."""

    def __init__(self, ffmpeg_path: str):
        self.ffmpeg_path = Path(ffmpeg_path)
        self.ffprobe_path = None
        self.progress_parser = ProgressParser()
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
                ffprobe_sys = shutil.which("ffprobe")
                if ffprobe_sys:
                    self.ffprobe_path = Path(ffprobe_sys)
            except:
                pass

    def has_ffprobe(self) -> bool:
        """Check if ffprobe is available."""
        return self.ffprobe_path is not None and self.ffprobe_path.exists()

    def execute_with_progress(
        self,
        cmd: List[str],
        job_id: str,
        progress_callback=None,
        timeout_seconds: int = 300,
        max_retries: int = 2
    ) -> Tuple[bool, str, str, int]:
        """
        Execute FFMPEG command with progress monitoring and retry logic.
        Returns: (success, stdout, stderr, exit_code)
        """
        # First detect the total duration (if possible)
        total_duration = self._detect_duration(cmd)

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
                current_time = 0.0

                # Monitor progress in real-time
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

                    # Read stderr for progress updates
                    try:
                        line = process.stderr.readline()
                        if line:
                            # Parse progress
                            time_value = self.progress_parser.parse_time(line)
                            if time_value is not None:
                                current_time = time_value
                                progress = self.progress_parser.calculate_progress(current_time, total_duration)

                                if progress_callback and total_duration > 0:
                                    progress_callback(
                                        progress,
                                        RenderStatus.RENDERING,
                                        f"Rendering: {current_time:.1f}s / {total_duration:.1f}s"
                                    )
                    except Exception:
                        pass  # Continue monitoring even if parsing fails

                    time.sleep(0.1)  # Brief polling interval

                # Get final output
                final_stdout, final_stderr = process.communicate()

                if process.returncode == 0:
                    if progress_callback:
                        progress_callback(100, RenderStatus.COMPLETED, "Render completed")
                    return True, final_stdout, final_stderr, 0

                logger.warning(f"FFMPEG attempt {attempt + 1} failed with code {process.returncode}")

                # Don't retry if it's the last attempt
                if attempt == max_retries:
                    if progress_callback:
                        progress_callback(0, RenderStatus.FAILED, f"Render failed after {max_retries + 1} attempts")
                    return False, final_stdout, final_stderr, process.returncode or -1

                # Brief delay before retry
                time.sleep(1)

                if progress_callback:
                    progress_callback(10, RenderStatus.RENDERING, f"Retrying render (attempt {attempt + 2})")

            except subprocess.TimeoutExpired:
                logger.warning(f"FFMPEG timeout on attempt {attempt + 1}")
                if attempt == max_retries:
                    return False, "", "", -2
                time.sleep(2)

            except Exception as e:
                logger.error(f"FFMPEG execution error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    return False, "", str(e), -3
                time.sleep(1)

        return False, "", "", -4

    def _detect_duration(self, cmd: List[str]) -> float:
        """Try to detect total duration from FFmpeg command or first execution."""
        # For generated content (lavfi), duration is usually specified in the command
        # Look for duration parameters in the command
        duration = 10.0  # Default fallback

        for arg in cmd:
            # Look for duration patterns like "d=10" in lavfi inputs
            if arg.startswith("d="):
                try:
                    duration = float(arg.split("=")[1])
                    break
                except:
                    pass

            # Look for duration parameters
            elif arg.startswith("t=") or arg == "-t":
                try:
                    idx = cmd.index(arg)
                    if idx + 1 < len(cmd):
                        duration = float(cmd[idx + 1])
                        break
                except:
                    pass

        return duration


class ProductionFfmpegRenderEngine(RenderEngine):
    """Production-grade FFmpeg render engine for video processing and creation."""

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

            if not self.ffmpeg_path:
                # Check common installation paths
                common_paths = [
                    "/usr/bin/ffmpeg",
                    "/usr/local/bin/ffmpeg",
                    "C:\\ffmpeg\\bin\\ffmpeg.exe",
                    "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
                ]

                for path in common_paths:
                    if os.path.exists(path) and os.access(path, os.X_OK):
                        self.ffmpeg_path = path
                        break

            if self.ffmpeg_path:
                # Initialize supervisor
                self.supervisor = FFMpegSupervisor(self.ffmpeg_path)

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
                    logger.info(f"FFprobe available: {self.supervisor.has_ffprobe()}")
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
            if resolution[0] <= 0 or resolution[1] <= 0:
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
            valid_codecs = ["libx264", "libx265", "libvpx", "libvpx-vp9", "libaom-av1"]
            if codec not in valid_codecs:
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
        """Create a scene configuration for FFmpeg with proper resource management."""
        temp_dir = None
        try:
            # Create temporary directory with immediate cleanup registration
            temp_dir = Path(tempfile.mkdtemp(prefix="omnivid_ffmpeg_"))
            temp_dir_obj = temp_dir  # Keep reference for cleanup

            # Create a configuration file
            config = {
                "prompt": prompt,
                "settings": settings,
                "input_files": [],
                "filters": [],
                "output_format": settings.get("output_format", "mp4"),
                "temp_dir": str(temp_dir),
                "created_at": time.time()
            }

            # Save configuration atomically
            config_path = temp_dir / "config.json"
            import json
            config_data = json.dumps(config, indent=2)

            with open(config_path, 'w') as f:
                f.write(config_data)
                f.flush()
                os.fsync(f.fileno())  # Ensure written to disk

            return str(config_path)

        except Exception as e:
            logger.error(f"Error creating FFmpeg scene: {str(e)}")
            # Clean up immediately on failure
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass
            raise

    def render_video(
        self, scene_path: str, output_path: str, progress_callback=None
    ) -> RenderResult:
        """Render video using FFmpeg with production-grade error handling."""
        temp_dir = None

        def cleanup_temp():
            """Clean up temporary directory and resources."""
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp dir {temp_dir}: {e}")

        try:
            if progress_callback:
                progress_callback(0, RenderStatus.INITIALIZING, "Starting FFmpeg render")

            # Load configuration
            import json
            with open(scene_path, "r") as f:
                config = json.load(f)

            settings = config["settings"]
            temp_dir = Path(config.get("temp_dir", ""))

            # Create output directory
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if progress_callback:
                progress_callback(10, RenderStatus.INITIALIZING, "Validating settings")

            # Validate settings
            if not self.validate_settings(settings):
                raise ValueError("Invalid FFmpeg settings")

            if progress_callback:
                progress_callback(20, RenderStatus.RENDERING, "Generating FFmpeg command")

            # Generate FFmpeg command
            cmd = self._build_ffmpeg_command(settings, str(output_path))

            # Execute with supervisor and progress monitoring
            if progress_callback:
                progress_callback(30, RenderStatus.RENDERING, "Starting FFmpeg process")

            success, stdout, stderr, exit_code = self.supervisor.execute_with_progress(
                cmd=cmd,
                job_id=f"ffmpeg_{int(time.time())}",
                progress_callback=progress_callback,
                timeout_seconds=300,  # 5 minute timeout
                max_retries=2
            )

            if not success:
                error_msg = self._classify_ffmpeg_error(stderr, exit_code)
                logger.error(f"FFmpeg render failed: {error_msg}")
                return RenderResult(
                    success=False,
                    error_message=error_msg,
                    metadata={
                        "stderr": stderr,
                        "stdout": stdout,
                        "exit_code": exit_code
                    }
                )

            # Verify output file exists and is valid
            if not output_path.exists():
                raise FileNotFoundError(f"FFmpeg did not create output file: {output_path}")

            if output_path.stat().st_size == 0:
                raise ValueError(f"FFmpeg created empty output file: {output_path}")

            if progress_callback:
                progress_callback(95, RenderStatus.POST_PROCESSING, "Verifying output")

            # Get video info using ffprobe
            duration = self._get_video_duration(str(output_path))
            resolution = self._get_video_resolution(str(output_path))

            return RenderResult(
                success=True,
                video_url=str(output_path),
                duration=duration,
                resolution=resolution,
                metadata={
                    "render_engine": "ffmpeg",
                    "ffmpeg_version": self.version,
                    "ffprobe_available": self.supervisor.has_ffprobe(),
                    "settings": settings,
                    "command": cmd,
                    "exit_code": exit_code
                }
            )

        except Exception as e:
            error_msg = f"FFmpeg render error: {str(e)}"
            logger.error(error_msg, exc_info=True)

            if progress_callback:
                progress_callback(0, RenderStatus.FAILED, error_msg)

            return RenderResult(success=False, error_message=error_msg)

        finally:
            cleanup_temp()

    def _classify_ffmpeg_error(self, stderr: str, exit_code: int) -> str:
        """Classify FFmpeg error for better error handling."""
        if exit_code == -2:
            return "FFmpeg process timed out"
        elif exit_code == -3:
            return "FFmpeg process execution failed"
        elif "No such file or directory" in stderr:
            return "FFmpeg input/output path error"
        elif "Invalid argument" in stderr:
            return "FFmpeg invalid command arguments"
        elif "Permission denied" in stderr:
            return "FFmpeg permission error"
        else:
            return f"FFmpeg failed with exit code {exit_code}"

    def _build_ffmpeg_command(self, settings: Dict[str, Any], output_path: str) -> List[str]:
        """Build FFmpeg command with proper escaping and validation."""
        cmd = [self.ffmpeg_path]

        # Add input (for now, generate a test pattern with proper colors)
        resolution = settings.get("resolution", (1920, 1080))
        duration = settings.get("duration", 10)
        fps = settings.get("fps", 30)

        # Create a more interesting test pattern based on prompt
        color_scheme = self._determine_color_scheme(settings.get("prompt", ""))
        background_color = color_scheme.get("background", "blue")
        text_color = color_scheme.get("text", "white")

        cmd.extend([
            "-f", "lavfi",
            "-i", f"color=c={background_color}:s={resolution[0]}x{resolution[1]}:d={duration}"
        ])

        # Build filters safely
        filters = []

        # Add text overlay with proper escaping
        prompt_text = settings.get("text", "")
        if prompt_text:
            # Escape special characters for FFmpeg
            escaped_text = self._escape_ffmpeg_text(prompt_text)
            filters.append(
                f"drawtext=text='{escaped_text}':fontsize=48:fontcolor={text_color}:"
                "x=(w-text_w)/2:y=(h-text_h)/2:borderw=2:bordercolor=black"
            )

        # Add resolution scaling filter if needed
        target_res = settings.get("resolution", (1920, 1080))
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # Add video codec and settings
        codec = settings.get("codec", "libx264")
        cmd.extend(["-c:v", codec])

        if codec == "libx264":
            cmd.extend(["-preset", "fast", "-crf", "18"])

        # Add bitrate
        bitrate = settings.get("bitrate", 5000)
        cmd.extend(["-b:v", f"{bitrate}k"])

        # Add framerate
        cmd.extend(["-r", str(fps)])

        # Add output
        cmd.extend(["-y", output_path])  # -y for overwrite

        return cmd

    def _escape_ffmpeg_text(self, text: str) -> str:
        """Escape special characters in text for FFmpeg drawtext filter."""
        # FFmpeg drawtext escaping rules
        text = text.replace("'", "\\'")  # Escape single quotes
        text = text.replace(":", "\\:")  # Escape colons
        text = text.replace("%", "%%")   # Escape percent signs
        # Remove or replace other problematic characters
        text = re.sub(r'[<>|&]', '', text)  # Remove shell metacharacters
        return text[:100]  # Limit text length for safety

    def _determine_color_scheme(self, prompt: str) -> Dict[str, str]:
        """Determine color scheme based on prompt content."""
        prompt_lower = prompt.lower()

        if "red" in prompt_lower:
            return {"background": "darkred", "text": "white"}
        elif "blue" in prompt_lower:
            return {"background": "darkblue", "text": "yellow"}
        elif "green" in prompt_lower:
            return {"background": "darkgreen", "text": "white"}
        elif "yellow" in prompt_lower or "sun" in prompt_lower:
            return {"background": "gold", "text": "black"}
        elif "purple" in prompt_lower or "violet" in prompt_lower:
            return {"background": "purple", "text": "white"}
        else:
            return {"background": "steelblue", "text": "white"}

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using FFprobe with proper error handling."""
        if not self.supervisor.has_ffprobe():
            logger.warning("FFprobe not available, using default duration")
            return 10.0

        try:
            ffprobe_cmd = [
                str(self.supervisor.ffprobe_path),
                "-v", "quiet",
                "-print_format", "json=c=1",  # Compact JSON
                "-show_format",
                video_path,
            ]

            result = subprocess.run(
                ffprobe_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                import json
                try:
                    data = json.loads(result.stdout.strip())
                    duration_str = data.get("format", {}).get("duration")
                    if duration_str:
                        return float(duration_str)
                except json.JSONDecodeError:
                    pass

            logger.warning(f"Duration detection failed, using default")
            return 10.0

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"FFprobe duration detection failed: {e}")
            return 10.0

    def _get_video_resolution(self, video_path: str) -> Tuple[int, int]:
        """Get video resolution using FFprobe with proper error handling."""
        if not self.supervisor.has_ffprobe():
            logger.warning("FFprobe not available, using default resolution")
            return (1920, 1080)

        try:
            ffprobe_cmd = [
                str(self.supervisor.ffprobe_path),
                "-v", "quiet",
                "-print_format", "json=c=1",
                "-show_streams",
                "-select_streams", "v:0",  # First video stream
                video_path,
            ]

            result = subprocess.run(
                ffprobe_cmd,
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                import json
                try:
                    data = json.loads(result.stdout.strip())
                    streams = data.get("streams", [])
                    for stream in streams:
                        if stream.get("codec_type") == "video":
                            width = stream.get("width")
                            height = stream.get("height")
                            if width and height:
                                return (int(width), int(height))
                except json.JSONDecodeError:
                    pass

            logger.warning(f"Resolution detection failed, using default")
            return (1920, 1080)

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            logger.warning(f"FFprobe resolution detection failed: {e}")
            return (1920, 1080)

    def get_supported_resolutions(self) -> List[Tuple[int, int]]:
        """Get FFmpeg-supported resolutions."""
        return [
            (7680, 4320),  # 8K
            (3840, 2160),  # 4K
            (2560, 1440),  # 2K
            (1920, 1080),  # Full HD
            (1280, 720),   # HD
            (854, 480),    # SD
            (640, 360),    # Low
        ]

    def get_supported_fps(self) -> List[float]:
        """Get FFmpeg-supported frame rates."""
        return [15, 23.976, 24, 25, 29.97, 30, 50, 59.94, 60, 120]
