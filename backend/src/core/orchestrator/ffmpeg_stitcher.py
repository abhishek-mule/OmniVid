"""
FFmpeg Stitcher: Combines rendered video clips into final output.
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class FFmpegStitcher:
    """Handles video stitching and post-processing using FFmpeg."""

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable."""
        # Try common paths
        common_paths = [
            "ffmpeg",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",  # Windows
        ]

        for path in common_paths:
            if self._check_ffmpeg_available(path):
                return path

        logger.warning("FFmpeg not found in common paths")
        return "ffmpeg"  # Hope it's in PATH

    def _check_ffmpeg_available(self, path: str) -> bool:
        """Check if FFmpeg is available at the given path."""
        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def stitch_videos(self, video_files: List[str], output_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stitch multiple video files into a single output video.

        Args:
            video_files: List of input video file paths
            output_path: Output video file path
            settings: Stitching settings (transitions, audio, etc.)

        Returns:
            Dict with stitching result info
        """
        if len(video_files) == 1:
            # Single video, just copy with potential re-encoding
            return self._copy_video(video_files[0], output_path, settings)

        elif len(video_files) == 2:
            # Two videos - use crossfade transition
            return self._crossfade_videos(video_files[0], video_files[1], output_path, settings)

        else:
            # Multiple videos - concatenate with transitions
            return self._concatenate_videos(video_files, output_path, settings)

    def _copy_video(self, input_path: str, output_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Copy video with optional re-encoding."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Simple copy for now - could add re-encoding options later
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-c", "copy",  # Copy streams without re-encoding
            "-y",  # Overwrite output
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output_path": output_path,
                    "duration": self._get_video_duration(output_path)
                }
            else:
                logger.error(f"FFmpeg copy failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "FFmpeg copy timed out"}

    def _crossfade_videos(self, video1: str, video2: str, output_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create crossfade transition between two videos."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get video info
        duration1 = self._get_video_duration(video1)
        duration2 = self._get_video_duration(video2)

        # Crossfade settings
        fade_duration = min(settings.get("transition_duration", 1.0), duration1, duration2)
        total_duration = duration1 + duration2 - fade_duration

        # FFmpeg complex filter for crossfade
        filter_complex = (
            f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={duration1 - fade_duration}[v];"
            f"[0:a][1:a]acrossfade=d={fade_duration}:c1=tri:c2=tri[a]"
        )

        cmd = [
            self.ffmpeg_path,
            "-i", video1,
            "-i", video2,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-y",
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output_path": output_path,
                    "duration": total_duration,
                    "transition": "crossfade"
                }
            else:
                logger.error(f"FFmpeg crossfade failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "FFmpeg crossfade timed out"}

    def _concatenate_videos(self, video_files: List[str], output_path: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Concatenate multiple videos with simple cuts."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create concat file
        concat_file = self._create_concat_file(video_files)

        cmd = [
            self.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",  # Copy streams
            "-y",
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                # Clean up concat file
                try:
                    os.remove(concat_file)
                except:
                    pass

                total_duration = sum(self._get_video_duration(v) for v in video_files)

                return {
                    "status": "success",
                    "output_path": output_path,
                    "duration": total_duration,
                    "videos_count": len(video_files)
                }
            else:
                logger.error(f"FFmpeg concatenate failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "FFmpeg concatenate timed out"}

    def _create_concat_file(self, video_files: List[str]) -> str:
        """Create a concat file for FFmpeg."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for video_file in video_files:
                f.write(f"file '{video_file}'\n")
            return f.name

    def apply_video_filters(self, input_path: str, output_path: str, filters: List[str]) -> Dict[str, Any]:
        """Apply video filters to a rendered video."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build filter string
        filter_string = ",".join(filters)

        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vf", filter_string,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "22",
            "-c:a", "copy",
            "-y",
            output_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output_path": output_path,
                    "filters_applied": filters
                }
            else:
                logger.error(f"FFmpeg filters failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "FFmpeg filters timed out"}

    def optimize_video(self, input_path: str, output_path: str, target_bitrate: Optional[str] = None) -> Dict[str, Any]:
        """Optimize video for web delivery."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Default optimization settings
        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",  # Good quality/size balance
            "-vf", "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",  # Web optimization
            "-y",
            output_path
        ]

        # Add bitrate if specified
        if target_bitrate:
            cmd.extend(["-b:v", target_bitrate])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "output_path": output_path,
                    "optimized": True
                }
            else:
                logger.error(f"FFmpeg optimization failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": "FFmpeg optimization timed out"}

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe."""
        try:
            cmd = [
                self.ffmpeg_path.replace("ffmpeg", "ffprobe"),  # Use ffprobe
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                duration = float(data.get("format", {}).get("duration", 0))
                return duration
        except:
            pass

        # Fallback - try parsing filename or return default
        return 5.0

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get detailed video information."""
        try:
            cmd = [
                self.ffmpeg_path.replace("ffmpeg", "ffprobe"),
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-show_format",
                video_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except:
            pass

        return {"error": "Could not get video info"}

# Global instance
ffmpeg_stitcher = FFmpegStitcher()
