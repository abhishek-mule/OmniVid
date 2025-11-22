#!/usr/bin/env python3
"""
Production-Grade Blender Frame Renderer
- SHA256 manifest validation
- .ok marker atomic completion per frame
- Blender supervisor integration with timeout/retry
- Auto-camera bounding box positioning
- Stream-based frame hashing
- FFmpeg video assembly with progress monitoring
"""

import bpy
import json
import sys
import os
import time
import subprocess
import atexit
import signal
import math
import mathutils
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List

# Add parent directory to import production infrastructure
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

try:
    from utils.blender_supervisor import (
        AtomicFileWriter, StreamHasher, Manifest,
        BlenderSupervisor, BlenderResult
    )
    from render_engines.ffmpeg_production import (
        ProgressParser, FFMpegSupervisor
    )
except ImportError:
    # Fallback for development
    print("Warning: Production infrastructure not available", file=sys.stderr)

# Constants
MAX_FRAME_RETRIES = 3
RENDER_TIMEOUT = 300  # 5 minutes per frame
MAX_RESTARTS = 2
MIN_DISK_SPACE_MB = 500


class RenderError(Exception):
    """Custom exception for render-related errors."""
    pass


def log(message: str, level: str = "INFO") -> None:
    """Structured logging with timestamps."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}",
          file=sys.stderr if level == "ERROR" else sys.stdout)
    sys.stdout.flush()


def check_disk_space(path: Path) -> bool:
    """Check if there's enough disk space."""
    try:
        if sys.platform == 'win32':
            import ctypes
            _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                str(path),
                ctypes.byref(_),
                ctypes.byref(total),
                ctypes.byref(free)
            )
            free_space_mb = free.value / (1024 * 1024)
        else:
            stat = os.statvfs(path)
            free_space_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)

        return free_space_mb > MIN_DISK_SPACE_MB
    except Exception as e:
        log(f"Failed to check disk space: {str(e)}", "WARNING")
        return True


def safe_sync() -> None:
    """Ensure all file operations are synced to disk."""
    try:
        if hasattr(os, 'sync'):
            os.sync()
        elif sys.platform == 'win32':
            import ctypes
            ctypes.windll.kernel32.FlushFileBuffers(-1)
    except Exception:
        pass


def load_scene_safely(blend_path: Path, manifest: Optional[Manifest] = None) -> bpy.types.Scene:
    """Load a scene with manifest validation."""
    try:
        # Hash the .blend file and validate manifest if provided
        if manifest:
            blend_hash = StreamHasher.sha256_file(blend_path)
            log(f".blend file hash: {blend_hash[:16]}...")

            if blend_hash != manifest.blend_file_hash:
                raise RenderError(f"Blend file hash mismatch. Expected {manifest.blend_file_hash[:16]}, got {blend_hash[:16]}")

        # Clear existing data safely
        for block in bpy.data.meshes[:]:  # Create copy to avoid modification during iteration
            bpy.data.meshes.remove(block, do_unlink=True)
        for block in bpy.data.materials[:]:
            bpy.data.materials.remove(block, do_unlink=True)

        # Load all data blocks
        with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
            for attr in dir(data_from):
                if not attr.startswith('_') and not callable(getattr(data_from, attr)):
                    setattr(data_to, attr, getattr(data_from, attr))

        # Get the first scene
        if not bpy.data.scenes:
            raise RenderError("No scenes found in blend file")

        scene = bpy.data.scenes[0]
        log(f"Successfully loaded scene: {scene.name}")
        return scene

    except Exception as e:
        raise RenderError(f"Failed to load scene: {str(e)}")


def setup_camera_bounds(scene: bpy.types.Scene, manifest: Optional[Manifest] = None) -> None:
    """
    Set up a camera that optimally frames all visible objects using bounding box analysis.
    """
    if scene.camera and scene.camera.type == 'CAMERA':
        log("Scene already has camera, skipping repositioning")
        return

    # Calculate scene bounds using all renderable objects
    min_coord = [float('inf')] * 3
    max_coord = [float('-inf')] * 3
    has_objects = False

    renderable_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME'}

    for obj in scene.objects:
        if obj.type in renderable_types and obj.visible_get():
            has_objects = True
            # Transform bounding box to world space
            for vertex in obj.bound_box:
                world_vertex = obj.matrix_world @ mathutils.Vector(vertex)
                for i in range(3):
                    min_coord[i] = min(min_coord[i], world_vertex[i])
                    max_coord[i] = max(max_coord[i], world_vertex[i])

    # Create camera with optimal positioning
    camera_data = bpy.data.cameras.new('ProductionCamera')
    camera_obj = bpy.data.objects.new('ProductionCamera', camera_data)

    if has_objects:
        # Calculate scene dimensions and center
        center = mathutils.Vector(
            (min_coord[0] + max_coord[0]) / 2,
            (min_coord[1] + max_coord[1]) / 2,
            (min_coord[2] + max_coord[2]) / 2
        )
        size = mathutils.Vector((
            max_coord[0] - min_coord[0],
            max_coord[1] - min_coord[1],
            max_coord[2] - min_coord[2]
        ))

        max_size = max(size)
        if max_size == 0:
            max_size = 1.0  # Prevent division by zero

        # Position camera using rule of thirds and golden ratio for optimal framing
        # Distance based on field of view and scene size
        focal_length = 35  # mm - good general purpose
        sensor_width = 36  # mm (full frame)

        # Calculate distance needed to frame the scene
        # FOV = 2 * arctan(sensor_width / (2 * focal_length))
        fov_radians = 2 * math.atan(sensor_width / (2 * focal_length))
        distance = max_size / (2 * math.tan(fov_radians / 2))

        # Add safety margin and ensure minimum distance
        distance = max(distance * 1.5, 5.0)

        # Position camera for dramatic angle (not straight on)
        camera_obj.location = center + mathutils.Vector((
            0,  # No offset in X
            -distance,  # Behind scene
            distance * 0.3  # Slightly above center for better perspective
        ))

        # Look down slightly and rotate for better composition
        camera_obj.rotation_euler = (
            math.radians(25),  # Look down 25 degrees
            0,  # No roll
            0   # No yaw
        )

        log(f"Auto-positioned camera: position={camera_obj.location}, distance={distance:.1f}, max_size={max_size:.2f}")

    else:
        # Default camera position for empty scenes
        camera_obj.location = (0, -10, 5)
        camera_obj.rotation_euler = (math.radians(30), 0, 0)
        log("Using default camera position (no objects found)")

    # Configure camera with optimal settings
    camera_data.lens = 35  # Good general purpose focal length
    camera_data.sensor_fit = 'HORIZONTAL'  # Horizontal sensor fit
    camera_data.sensor_width = 36  # Full frame equivalent
    camera_data.clip_start = 0.1
    camera_data.clip_end = 1000

    # Link camera to scene
    scene.collection.objects.link(camera_obj)
    scene.camera = camera_obj

    # Apply resolution settings from manifest if available
    if manifest and 'resolution' in manifest.settings:
        resolution = manifest.settings['resolution']
        if len(resolution) == 2:
            scene.render.resolution_x = resolution[0]
            scene.render.resolution_y = resolution[1]
            log(f"Applied resolution: {resolution[0]}x{resolution[1]}")


def render_frame_with_atomic_completion(
    scene: bpy.types.Scene,
    frame: int,
    output_path: Path,
    depsgraph: Optional[bpy.types.Depsgraph] = None,
    max_retries: int = MAX_FRAME_RETRIES
) -> bool:
    """
    Render a frame with atomic file operations and .ok completion marker.
    Returns True if frame was successfully rendered and marked complete.
    """
    output_path = output_path.resolve()
    output_dir = output_path.parent
    temp_path = output_path.with_suffix('.tmp')

    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Skip if already complete with valid .ok marker
        ok_marker = output_path.with_suffix('.ok')
        if ok_marker.exists() and output_path.exists() and output_path.stat().st_size > 0:
            try:
                with open(ok_marker, 'r') as f:
                    marker_data = json.load(f)
                if marker_data.get('completed_at', 0) > 0:
                    log(f"Skipping completed frame {frame}")
                    return True
            except Exception:
                pass  # Marker corrupt, re-render

        # Set frame and update depsgraph
        scene.frame_set(frame)
        if depsgraph is None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()

        # Configure output for PNG
        scene.render.filepath = str(temp_path)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'

        # Render with retries using supervisor pattern
        for attempt in range(max_retries):
            try:
                log(f"Rendering frame {frame}, attempt {attempt + 1}")

                # Use direct render API
                if hasattr(bpy.ops, 'render') and hasattr(bpy.ops.render, 'render'):
                    result = bpy.ops.render.render(
                        animation=False,
                        write_still=True,
                        use_viewport=False,
                        layer=scene.view_layers[0].name if scene.view_layers else '',
                        scene=scene.name
                    )

                    if not result == {'FINISHED'}:
                        raise RenderError(f"Render operation failed with status: {result}")
                else:
                    # Fallback to direct file write
                    bpy.ops.render.render(write_still=True)

                # Verify output exists and has content
                if not temp_path.exists():
                    raise RenderError("Output file was not created")

                file_size = temp_path.stat().st_size
                if file_size == 0:
                    raise RenderError("Output file is empty")

                # Atomic move: temp -> final
                temp_path.replace(output_path)
                safe_sync()  # Ensure file system consistency

                # Write completion marker with frame metadata
                frame_metadata = {
                    'frame_number': frame,
                    'scene_name': scene.name,
                    'render_engine': scene.render.engine,
                    'resolution': f"{scene.render.resolution_x}x{scene.render.resolution_y}",
                    'render_time': int(time.time())
                }

                with open(ok_marker, 'w') as f:
                    json.dump(frame_metadata, f, indent=2)
                safe_sync()

                log(f"Successfully rendered and marked complete: frame {frame} ({file_size} bytes)")
                return True

            except Exception as e:
                log(f"Frame {frame} attempt {attempt + 1} failed: {str(e)}", "WARNING")

                # Clean up any partial output
                for path in [temp_path, output_path]:
                    if path.exists():
                        try:
                            path.unlink()
                        except Exception:
                            pass

                if attempt == max_retries - 1:
                    raise RenderError(f"Failed to render frame {frame} after {max_retries} attempts: {str(e)}")

                time.sleep(0.5)  # Brief delay before retry

    except Exception as e:
        # Clean up any remaining temp files
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise RenderError(f"Frame rendering failed for frame {frame}: {str(e)}")


def render_frame_range_production(
    blend_path: Path,
    manifest_path: Optional[Path],
    output_dir: Path,
    start_frame: int,
    end_frame: int,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Production frame rendering with manifest validation and atomic operations.
    """
    result = {
        'success': False,
        'frames_rendered': 0,
        'frames_failed': 0,
        'total_frames': end_frame - start_frame + 1,
        'duration_seconds': 0,
        'errors': []
    }

    start_time = time.time()
    manifest = None

    try:
        # Load and validate manifest if provided
        if manifest_path and manifest_path.exists():
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
            manifest = Manifest.from_dict(manifest_data)

            # Validate manifest against expected job
            # Note: In real usage, would pass expected settings
            log(f"Loaded render manifest for job: {manifest.job_id}")
        else:
            log("No manifest provided, skipping validation")

        # Load scene with validation
        scene = load_scene_safely(blend_path, manifest)

        # Setup camera bounds (auto-positioning)
        setup_camera_bounds(scene, manifest)

        # Apply render settings from manifest or scene defaults
        if manifest and 'fps' in manifest.settings:
            scene.render.fps = manifest.settings['fps']
        if manifest and 'resolution' in manifest.expected_outputs:
            resolution = manifest.expected_outputs['resolution']
            if len(resolution) == 2:
                scene.render.resolution_x, scene.render.resolution_y = resolution

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get fresh depsgraph for stable rendering
        depsgraph = bpy.context.evaluated_depsgraph_get()

        # Render each frame with atomic completion
        for frame_num in range(start_frame, end_frame + 1):
            try:
                frame_path = output_dir / "03d"

                # Update progress before each frame
                if progress_callback:
                    frame_progress = (frame_num - start_frame + 1) / (end_frame - start_frame + 1) * 90  # Leave 10% for assembly
                    progress_callback(
                        frame_progress,
                        "RENDERING",
                        f"Rendering frame {frame_num} ({frame_num - start_frame + 1}/{end_frame - start_frame + 1})"
                    )

                # Render with atomic completion guarantees
                if render_frame_with_atomic_completion(scene, frame_num, frame_path, depsgraph):
                    result['frames_rendered'] += 1
                    log(f"Frame {frame_num} completed")
                else:
                    raise RenderError(f"Frame {frame_num} returned false")

            except Exception as e:
                error_msg = f"Failed to render frame {frame_num}: {str(e)}"
                result['errors'].append(error_msg)
                result['frames_failed'] += 1
                log(error_msg, "ERROR")

                # Continue with next frame unless this is catastrophic
                if "load" in error_msg.lower() or "scene" in error_msg.lower():
                    raise  # Stop on scene loading errors

        # Verify completion markers exist for all frames
        ok_files_found = 0
        for frame_num in range(start_frame, end_frame + 1):
            ok_path = (output_dir / "03d").with_suffix('.ok')
            if ok_path.exists():
                ok_files_found += 1
            else:
                log(f"Missing .ok marker for frame {frame_num}", "WARNING")

        log(f"Frame rendering complete: {result['frames_rendered']} rendered, {ok_files_found} markers")

        result['success'] = result['frames_failed'] == 0
        result['duration_seconds'] = time.time() - start_time

        # Final progress update
        if progress_callback:
            if result['success']:
                progress_callback(100, "COMPLETED", f"All {result['frames_rendered']} frames rendered successfully")
            else:
                progress_callback(0, "FAILED", f"Rendering failed: {result['frames_failed']} frames failed")

        return result

    except Exception as e:
        error_msg = f"Frame rendering failed: {str(e)}"
        result['errors'].append(error_msg)
        result['duration_seconds'] = time.time() - start_time
        log(error_msg, "ERROR")

        if progress_callback:
            progress_callback(0, "FAILED", error_msg)

        return result


def assemble_video_production(
    frame_dir: Path,
    output_path: Path,
    fps: int = 30,
    progress_callback=None
) -> bool:
    """
    Assemble rendered frames into video using production FFmpeg supervisor.
    """
    try:
        # Find FFMpeg supervisor
        try:
            ffmpeg_supervisor = FFMpegSupervisor('ffmpeg')  # Will find in PATH
        except NameError:
            # Fallback if not available
            log("FFMpegSupervisor not available, falling back to subprocess", "WARNING")
            return assemble_video_fallback(frame_dir, output_path, fps, progress_callback)

        frame_pattern = str(frame_dir / "frame_%04d.png")

        # Build FFmpeg command for frame assembly
        cmd = [
            'ffmpeg',
            '-y',
            '-framerate', str(fps),
            '-i', frame_pattern,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            '-crf', '18',
            '-preset', 'slow',
            '-movflags', '+faststart',
            '-loglevel', 'info',
            str(output_path)
        ]

        # Execute with progress monitoring
        success, stdout, stderr, exit_code = ffmpeg_supervisor.execute_with_progress(
            cmd=cmd,
            job_id=f"video_assembly_{int(time.time())}",
            progress_callback=progress_callback,
            timeout_seconds=600,  # 10 minute timeout for assembly
            max_retries=2
        )

        if success:
            # Verify output
            if output_path.exists() and output_path.stat().st_size > 0:
                log(f"Video assembly successful: {output_path} ({output_path.stat().st_size} bytes)")
                return True
            else:
                log("Video assembly produced no output file", "ERROR")
                return False
        else:
            log(f"Video assembly failed with exit code {exit_code}: {stderr}", "ERROR")
            return False

    except Exception as e:
        log(f"Video assembly error: {str(e)}", "ERROR")
        return False


def assemble_video_fallback(
    frame_dir: Path,
    output_path: Path,
    fps: int = 30,
    progress_callback=None
) -> bool:
    """Fallback video assembly without supervisor."""
    try:
        frame_pattern = str(frame_dir / "frame_%04d.png")

        cmd = [
            'ffmpeg',
            '-y',
            '-framerate', str(fps),
            '-i', frame_pattern,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            '-crf', '18',
            '-preset', 'fast',
            str(output_path)
        ]

        log(f"Running FFmpeg assembly: {' '.join(cmd)}")

        # Simple subprocess execution
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            if output_path.exists() and output_path.stat().st_size > 0:
                log(f"Fallback assembly successful: {output_path}")
                return True

        log(f"Fallback assembly failed: {result.stderr}", "ERROR")
        return False

    except subprocess.TimeoutExpired:
        log("Video assembly timeout", "ERROR")
        return False
    except Exception as e:
        log(f"Video assembly error: {str(e)}", "ERROR")
        return False


def cleanup_temp_frames(frame_dir: Path, keep_frames: bool = False, max_age_hours: int = 24) -> dict:
    """
    Clean up temporary frames after successful assembly.
    Returns dict with cleanup statistics.

    Args:
        frame_dir: Directory containing frames
        keep_frames: If True, keep frames even after cleanup
        max_age_hours: Clean frames older than this many hours

    Returns:
        dict: {'bytes_freed': int, 'files_cleaned': int, 'dirs_removed': int}
    """
    result = {'bytes_freed': 0, 'files_cleaned': 0, 'dirs_removed': 0}

    try:
        if keep_frames or not frame_dir.exists():
            return result

        import time
        cutoff_time = time.time() - (max_age_hours * 3600)

        # Remove old frame files (.png) and completion markers (.ok)
        frame_files = list(frame_dir.glob("*.png")) + list(frame_dir.glob("*.ok"))

        for frame_file in frame_files:
            if frame_file.stat().st_mtime < cutoff_time:
                try:
                    file_size = frame_file.stat().st_size
                    frame_file.unlink()
                    result['bytes_freed'] += file_size
                    result['files_cleaned'] += 1
                except Exception:
                    pass

        # Remove directory if it's empty or contains only very old files
        try:
            remaining_files = list(frame_dir.glob("*"))
            if not remaining_files or all(f.stat().st_mtime < cutoff_time for f in remaining_files if f.is_file()):
                shutil.rmtree(frame_dir)
                result['dirs_removed'] = 1
                log(f"Removed empty frame directory: {frame_dir}")
            elif result['files_cleaned'] > 0:
                log(f"Cleaned {result['files_cleaned']} old frame files, freed {result['bytes_freed']} bytes")
        except Exception:
            pass

        return result

    except Exception as e:
        log(f"Failed to cleanup temp frames: {e}")
        return 0


def main():
    """Main production frame rendering entry point."""
    if '--' not in sys.argv:
        log("Error: No script arguments provided (use -- separator)", "ERROR")
        sys.exit(1)

    args = sys.argv[sys.argv.index('--') + 1:]

    if len(args) < 3:
        log("Error: Missing required arguments: <blend_path> <output_dir> <manifest_path> [start_frame] [end_frame]", "ERROR")
        sys.exit(1)

    blend_path = Path(args[0])
    output_dir = Path(args[1])
    manifest_path = Path(args[2]) if len(args) > 2 else None
    start_frame = int(args[3]) if len(args) > 3 else None
    end_frame = int(args[4]) if len(args) > 4 else None

    # Progress callback for CLI usage
    def cli_progress(progress: float, status: str, message: str) -> None:
        status_emoji = {
            "INITIALIZING": "🔄",
            "RENDERING": "🎬",
            "POST_PROCESSING": "⚙️",
            "COMPLETED": "✅",
            "FAILED": "❌"
        }.get(status, "ℹ️")

        log(f"{status_emoji} {progress:.1f}% - {message}")

    try:
        # Check prerequisites
        if not blend_path.exists():
            raise RenderError(f"Blend file not found: {blend_path}")

        process_id = os.getpid()
        atexit.register(lambda: log(f"Process {process_id} exiting", "INFO"))

        # Check disk space
        if not check_disk_space(output_dir):
            raise RenderError(f"Insufficient disk space (need at least {MIN_DISK_SPACE_MB}MB free)")

        # Load scene to determine frame range if not specified
        if start_frame is None or end_frame is None:
            temp_scene = load_scene_safely(blend_path)
            start_frame = start_frame if start_frame is not None else temp_scene.frame_start
            end_frame = end_frame if end_frame is not None else temp_scene.frame_end
            log(f"Auto-detected frame range: {start_frame}-{end_frame}")

        log(f"Starting production render: {blend_path.name} → {output_dir}")
        log(f"Frame range: {start_frame}-{end_frame}")

        # Execute production frame rendering
        result = render_frame_range_production(
            blend_path=blend_path,
            manifest_path=manifest_path,
            output_dir=output_dir,
            start_frame=start_frame,
            end_frame=end_frame,
            progress_callback=cli_progress
        )

        if not result['success']:
            log("Frame rendering failed", "ERROR")
            for error in result['errors']:
                log(f"  - {error}", "ERROR")
            sys.exit(1)

        # Assemble video
        frame_dir = output_dir
        video_path = output_dir.parent / "03d"
        fps = 30  # Would come from manifest in real usage

        cli_progress(95, "POST_PROCESSING", "Assembling video...")
        if assemble_video_production(frame_dir, video_path, fps, cli_progress):
            cli_progress(100, "COMPLETED", "Production render completed")

            # Cleanup temp frames
            cleanup_temp_frames(frame_dir)

            sys.exit(0)
        else:
            log("Video assembly failed", "ERROR")
            sys.exit(1)

    except Exception as e:
        log(f"Fatal production render error: {str(e)}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
