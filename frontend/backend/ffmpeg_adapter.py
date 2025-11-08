"""
FFmpegAdapter

Concrete implementation of BaseEngine for FFmpeg video processing.
Handles video composition, transitions, effects, and final assembly.
"""

import subprocess
import uuid
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from threading import Thread

from base_engine import (
    BaseEngine,
    EngineType,
    RenderConfig,
    RenderResult,
    RenderStatus
)


class FFmpegAdapter(BaseEngine):
    """
    Adapter for FFmpeg video processing engine.
    
    Provides video composition, transitions, filters, and assembly capabilities.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe", **kwargs):
        """
        Initialize the FFmpeg adapter.
        
        Args:
            ffmpeg_path: Path to ffmpeg executable
            ffprobe_path: Path to ffprobe executable
            **kwargs: Additional configuration
        """
        super().__init__(EngineType.FFMPEG, **kwargs)
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self._render_jobs = {}
        self._input_files = []
        self._filter_complex = []
        self._concat_list = []
        
    def initialize(self) -> bool:
        """Initialize the FFmpeg engine."""
        try:
            validation = self.validate_environment()
            if not validation["valid"]:
                print(f"Environment validation failed: {validation['issues']}")
                return False
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate that FFmpeg environment is correctly configured."""
        issues = []
        version = None
        
        try:
            # Check FFmpeg
            ffmpeg_result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ffmpeg_result.returncode == 0:
                version_line = ffmpeg_result.stdout.split('\n')[0]
                version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else "unknown"
            else:
                issues.append("FFmpeg not found or not working")
            
            # Check FFprobe
            ffprobe_result = subprocess.run(
                [self.ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ffprobe_result.returncode != 0:
                issues.append("FFprobe not found or not working")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "version": version
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "version": None
            }
    
    def create_project(self, project_name: str, **kwargs) -> Any:
        """
        Create a new FFmpeg project context.
        
        Args:
            project_name: Name of the project
            **kwargs: Additional parameters
            
        Returns:
            Project identifier
        """
        project_id = str(uuid.uuid4())
        self._current_project = {
            "id": project_id,
            "name": project_name,
            "inputs": [],
            "filters": [],
            "metadata": kwargs
        }
        return project_id
    
    def add_asset(self, asset_path: str, asset_type: str, **kwargs) -> str:
        """
        Add an input file to the FFmpeg processing pipeline.
        
        Args:
            asset_path: Path to the input file
            asset_type: Type of asset (video, audio, image, etc.)
            **kwargs: Additional parameters (duration, loop, etc.)
            
        Returns:
            Asset identifier
        """
        asset_id = kwargs.get("asset_id", str(uuid.uuid4()))
        
        try:
            asset_info = {
                "id": asset_id,
                "path": asset_path,
                "type": asset_type,
                "duration": kwargs.get("duration"),
                "loop": kwargs.get("loop", False),
                "start_time": kwargs.get("start_time", 0),
                "metadata": self._probe_file(asset_path) if os.path.exists(asset_path) else None
            }
            
            self._input_files.append(asset_info)
            return asset_id
            
        except Exception as e:
            print(f"Error adding asset: {e}")
            return ""
    
    def add_scene(self, scene_config: Dict[str, Any]) -> str:
        """
        Add a scene configuration for processing.
        
        In FFmpeg context, scenes are segments that will be concatenated.
        
        Args:
            scene_config: Scene configuration
            
        Returns:
            Scene identifier
        """
        scene_id = scene_config.get("id", str(uuid.uuid4()))
        
        # Store scene for concatenation
        self._concat_list.append({
            "id": scene_id,
            "config": scene_config,
            "duration": scene_config.get("duration", 0)
        })
        
        return scene_id
    
    def apply_effect(self, target_id: str, effect_type: str, **params) -> bool:
        """
        Apply a video/audio effect using FFmpeg filters.
        
        Args:
            target_id: Target input/stream ID
            effect_type: Effect type (blur, fade, scale, overlay, etc.)
            **params: Effect parameters
            
        Returns:
            Success status
        """
        try:
            filter_str = self._build_filter(effect_type, **params)
            
            self._filter_complex.append({
                "target": target_id,
                "type": effect_type,
                "filter": filter_str,
                "params": params
            })
            
            return True
            
        except Exception as e:
            print(f"Error applying effect: {e}")
            return False
    
    def animate(self, target_id: str, animation_config: Dict[str, Any]) -> bool:
        """
        Add animation using FFmpeg filters.
        
        Args:
            target_id: Target stream ID
            animation_config: Animation configuration
            
        Returns:
            Success status
        """
        anim_type = animation_config.get("type", "fade")
        
        # Map animation to FFmpeg filter
        if anim_type == "fade":
            return self.apply_effect(
                target_id,
                "fade",
                type=animation_config.get("fade_type", "in"),
                start_time=animation_config.get("start_time", 0),
                duration=animation_config.get("duration", 1)
            )
        elif anim_type == "zoom":
            return self.apply_effect(
                target_id,
                "zoompan",
                zoom=animation_config.get("zoom_factor", 1.5),
                duration=animation_config.get("duration", 1)
            )
        
        return False
    
    def render(self, config: RenderConfig) -> RenderResult:
        """
        Render/process video using FFmpeg.
        
        Args:
            config: Rendering configuration
            
        Returns:
            Render result
        """
        if not self.validate_config(config):
            return RenderResult(
                status=RenderStatus.FAILED,
                error="Invalid render configuration"
            )
        
        try:
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(config)
            
            # Execute FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.additional_params.get("timeout", 600)
            )
            
            if result.returncode == 0:
                return RenderResult(
                    status=RenderStatus.COMPLETED,
                    output_path=config.output_path,
                    metadata={"stdout": result.stdout, "stderr": result.stderr}
                )
            else:
                return RenderResult(
                    status=RenderStatus.FAILED,
                    error=result.stderr,
                    metadata={"stdout": result.stdout}
                )
                
        except subprocess.TimeoutExpired:
            return RenderResult(
                status=RenderStatus.FAILED,
                error="Render timeout exceeded"
            )
        except Exception as e:
            return RenderResult(
                status=RenderStatus.FAILED,
                error=str(e)
            )
    
    def render_async(self, config: RenderConfig, callback: Optional[callable] = None) -> str:
        """
        Start asynchronous rendering operation.
        
        Args:
            config: Rendering configuration
            callback: Optional callback for progress updates
            
        Returns:
            Render job ID
        """
        job_id = str(uuid.uuid4())
        
        def render_thread():
            self._render_jobs[job_id] = {"status": RenderStatus.IN_PROGRESS}
            result = self.render(config)
            self._render_jobs[job_id] = {
                "status": result.status,
                "result": result
            }
            if callback:
                callback(job_id, result)
        
        thread = Thread(target=render_thread, daemon=True)
        thread.start()
        
        self._render_jobs[job_id] = {"status": RenderStatus.PENDING, "thread": thread}
        
        return job_id
    
    def get_render_status(self, job_id: str) -> RenderStatus:
        """Get the status of a render job."""
        job = self._render_jobs.get(job_id)
        if not job:
            return RenderStatus.FAILED
        return job.get("status", RenderStatus.FAILED)
    
    def cancel_render(self, job_id: str) -> bool:
        """Cancel a render job."""
        job = self._render_jobs.get(job_id)
        if not job:
            return False
        
        job["status"] = RenderStatus.CANCELLED
        return True
    
    def export_project(self, export_path: str, format: str = "json") -> bool:
        """Export project configuration."""
        try:
            export_data = {
                "engine": "ffmpeg",
                "inputs": self._input_files,
                "filters": self._filter_complex,
                "concat": self._concat_list,
                "project": self._current_project
            }
            
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def import_project(self, import_path: str) -> Any:
        """Import project configuration."""
        try:
            with open(import_path, "r") as f:
                data = json.load(f)
            
            if data.get("engine") != "ffmpeg":
                raise ValueError("Invalid project format")
            
            self._input_files = data.get("inputs", [])
            self._filter_complex = data.get("filters", [])
            self._concat_list = data.get("concat", [])
            self._current_project = data.get("project")
            
            return data
            
        except Exception as e:
            print(f"Import error: {e}")
            return None
    
    def cleanup(self) -> bool:
        """Clean up resources."""
        try:
            self._render_jobs.clear()
            self._input_files.clear()
            self._filter_complex.clear()
            self._concat_list.clear()
            self._initialized = False
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output formats for FFmpeg."""
        return ["mp4", "webm", "mov", "avi", "mkv", "flv", "gif", "mp3", "wav", "m4a"]
    
    def get_supported_codecs(self) -> List[str]:
        """Get supported codecs for FFmpeg."""
        return ["libx264", "libx265", "libvpx", "libvpx-vp9", "prores", "h264_nvenc", "hevc_nvenc"]
    
    # FFmpeg-specific methods
    
    def concat_videos(self, input_files: List[str], output_path: str, transition: Optional[str] = None) -> RenderResult:
        """
        Concatenate multiple video files.
        
        Args:
            input_files: List of input video paths
            output_path: Output file path
            transition: Optional transition effect (fade, wipe, etc.)
            
        Returns:
            Render result
        """
        try:
            if transition:
                # Use xfade filter for transitions
                return self._concat_with_transition(input_files, output_path, transition)
            else:
                # Simple concatenation
                return self._concat_simple(input_files, output_path)
                
        except Exception as e:
            return RenderResult(
                status=RenderStatus.FAILED,
                error=str(e)
            )
    
    def add_overlay(self, base_video: str, overlay_video: str, output_path: str, 
                    x: int = 0, y: int = 0, **kwargs) -> RenderResult:
        """
        Overlay one video on top of another.
        
        Args:
            base_video: Base video path
            overlay_video: Overlay video path
            output_path: Output file path
            x: X position
            y: Y position
            **kwargs: Additional parameters
            
        Returns:
            Render result
        """
        cmd = [
            self.ffmpeg_path,
            "-i", base_video,
            "-i", overlay_video,
            "-filter_complex", f"[0:v][1:v]overlay={x}:{y}",
            "-c:a", "copy",
            output_path,
            "-y"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return RenderResult(status=RenderStatus.COMPLETED, output_path=output_path)
            else:
                return RenderResult(status=RenderStatus.FAILED, error=result.stderr)
                
        except Exception as e:
            return RenderResult(status=RenderStatus.FAILED, error=str(e))
    
    def _probe_file(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata using ffprobe."""
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            
        except Exception as e:
            print(f"Error probing file: {e}")
        
        return {}
    
    def _build_filter(self, effect_type: str, **params) -> str:
        """Build FFmpeg filter string."""
        if effect_type == "blur":
            return f"boxblur={params.get('intensity', 5)}"
        elif effect_type == "fade":
            fade_type = params.get('type', 'in')
            start = params.get('start_time', 0)
            duration = params.get('duration', 1)
            return f"fade=t={fade_type}:st={start}:d={duration}"
        elif effect_type == "scale":
            width = params.get('width', -1)
            height = params.get('height', -1)
            return f"scale={width}:{height}"
        elif effect_type == "rotate":
            angle = params.get('angle', 0)
            return f"rotate={angle}*PI/180"
        
        return ""
    
    def _build_ffmpeg_command(self, config: RenderConfig) -> List[str]:
        """Build complete FFmpeg command."""
        cmd = [self.ffmpeg_path]
        
        # Add inputs
        for input_file in self._input_files:
            cmd.extend(["-i", input_file["path"]])
        
        # Add filter complex if exists
        if self._filter_complex:
            filter_str = ";".join([f["filter"] for f in self._filter_complex])
            cmd.extend(["-filter_complex", filter_str])
        
        # Video codec
        codec = config.codec or "libx264"
        cmd.extend(["-c:v", codec])
        
        # Quality (CRF)
        quality_map = {"low": 28, "medium": 23, "high": 18, "ultra": 15}
        crf = quality_map.get(config.quality, 23)
        if codec in ["libx264", "libx265"]:
            cmd.extend(["-crf", str(crf)])
        
        # Resolution
        cmd.extend(["-s", f"{config.width}x{config.height}"])
        
        # Frame rate
        cmd.extend(["-r", str(config.fps)])
        
        # Audio codec
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        
        # Output
        cmd.extend([config.output_path, "-y"])
        
        return cmd
    
    def _concat_simple(self, input_files: List[str], output_path: str) -> RenderResult:
        """Simple concatenation without transitions."""
        # Create concat file
        concat_file = f"concat_{uuid.uuid4()}.txt"
        
        try:
            with open(concat_file, "w") as f:
                for file_path in input_files:
                    f.write(f"file '{file_path}'\n")
            
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_path,
                "-y"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Cleanup
            os.remove(concat_file)
            
            if result.returncode == 0:
                return RenderResult(status=RenderStatus.COMPLETED, output_path=output_path)
            else:
                return RenderResult(status=RenderStatus.FAILED, error=result.stderr)
                
        except Exception as e:
            if os.path.exists(concat_file):
                os.remove(concat_file)
            return RenderResult(status=RenderStatus.FAILED, error=str(e))
    
    def _concat_with_transition(self, input_files: List[str], output_path: str, transition: str) -> RenderResult:
        """Concatenate with transition effects using xfade."""
        # Build xfade filter complex
        duration = 1.0  # Transition duration
        
        filter_parts = []
        for i in range(len(input_files) - 1):
            offset = i * 5  # Assume 5 seconds per clip (adjust as needed)
            filter_parts.append(f"[{i}:v][{i+1}:v]xfade=transition={transition}:duration={duration}:offset={offset}[v{i}]")
        
        cmd = [self.ffmpeg_path]
        
        # Add all inputs
        for file_path in input_files:
            cmd.extend(["-i", file_path])
        
        # Add filter complex
        filter_complex = ";".join(filter_parts)
        cmd.extend(["-filter_complex", filter_complex])
        
        # Output
        cmd.extend(["-map", f"[v{len(input_files)-2}]", output_path, "-y"])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return RenderResult(status=RenderStatus.COMPLETED, output_path=output_path)
            else:
                return RenderResult(status=RenderStatus.FAILED, error=result.stderr)
                
        except Exception as e:
            return RenderResult(status=RenderStatus.FAILED, error=str(e))
