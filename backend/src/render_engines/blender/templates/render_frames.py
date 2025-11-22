"""
Production-Grade Blender Frame Renderer
- Non-destructive scene loading
- Direct rendering API
- Robust error handling
- Process-safe operations
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
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List

# Constants
MAX_RETRIES = 3
RENDER_TIMEOUT = 300  # 5 minutes per frame
MAX_RESTARTS = 2
MIN_DISK_SPACE_MB = 500  # Minimum free disk space in MB

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
        return True  # Continue and fail later if disk is actually full

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

def load_scene_safely(blend_path: Path) -> bpy.types.Scene:
    """Load a scene without context-destructive operations."""
    try:
        # Clear existing data
        for block in bpy.data.meshes:
            bpy.data.meshes.remove(block, do_unlink=True)
        for block in bpy.data.materials:
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
        return scene
        
    except Exception as e:
        raise RenderError(f"Failed to load scene: {str(e)}")

def setup_camera_bounds(scene: bpy.types.Scene) -> None:
    """Set up a camera that frames all visible objects."""
    if scene.camera and scene.camera.type == 'CAMERA':
        return
    
    # Calculate scene bounds
    min_coord = [float('inf')] * 3
    max_coord = [float('-inf')] * 3
    has_objects = False
    
    for obj in scene.objects:
        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME'} and obj.visible_get():
            has_objects = True
            for vertex in obj.bound_box:
                world_vertex = obj.matrix_world @ mathutils.Vector(vertex)
                for i in range(3):
                    min_coord[i] = min(min_coord[i], world_vertex[i])
                    max_coord[i] = max(max_coord[i], world_vertex[i])
    
    # Create camera
    camera_data = bpy.data.cameras.new('RenderCamera')
    camera_obj = bpy.data.objects.new('RenderCamera', camera_data)
    
    if has_objects:
        # Position camera to frame all objects
        center = mathutils.Vector(
            (min_coord[0] + max_coord[0]) / 2,
            (min_coord[1] + max_coord[1]) / 2,
            (min_coord[2] + max_coord[2]) / 2
        )
        size = max((max_coord[i] - min_coord[i]) for i in range(3))
        
        # Position camera
        camera_distance = max(size * 1.5, 5.0)  # At least 5 units away
        camera_obj.location = center + mathutils.Vector((0, -camera_distance, camera_distance * 0.5))
        camera_obj.rotation_euler = (math.radians(60), 0, 0)  # Look down at 60 degrees
    else:
        # Default camera position
        camera_obj.location = (0, -10, 5)
        camera_obj.rotation_euler = (1.0, 0, 0)
    
    # Configure camera
    camera_data.lens = 35
    camera_data.sensor_fit = 'HORIZONTAL'
    camera_data.sensor_width = 36
    
    # Link camera to scene
    scene.collection.objects.link(camera_obj)
    scene.camera = camera_obj

def render_frame_direct(
    scene: bpy.types.Scene,
    frame: int,
    output_path: Path,
    depsgraph: Optional[bpy.types.Depsgraph] = None
) -> bool:
    """Render a frame using direct API calls."""
    output_path = output_path.resolve()
    output_dir = output_path.parent
    
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set frame and update depsgraph
        scene.frame_set(frame)
        if depsgraph is None:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            depsgraph.update()
        
        # Configure output
        scene.render.filepath = str(output_path)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '8'
        
        # Perform the render
        try:
            # Try direct render API first
            if hasattr(bpy.ops, 'render') and hasattr(bpy.ops.render, 'render'):
                result = bpy.ops.render.render(
                    animation=False,
                    write_still=True,
                    use_viewport=False,
                    layer=scene.view_layers[0].name,
                    scene=scene.name
                )
                
                if not result == {'FINISHED'}:
                    raise RenderError(f"Render operation failed with status: {result}")
            else:
                # Fallback to direct file write
                scene.render.filepath = str(output_path)
                bpy.ops.render.render(write_still=True)
            
            # Verify output
            if not output_path.exists():
                raise RenderError("Output file was not created")
                
            if output_path.stat().st_size == 0:
                raise RenderError("Output file is empty")
                
            # Ensure file is fully written
            safe_sync()
            return True
            
        except Exception as e:
            # Clean up partial output
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            raise
            
    except Exception as e:
        raise RenderError(f"Failed to render frame {frame}: {str(e)}")

def render_animation_worker(
    blend_path: Path,
    output_dir: Path,
    settings: Dict[str, Any],
    start_frame: int,
    end_frame: int,
    process_id: int = 0
) -> bool:
    """Worker function for rendering a range of frames."""
    try:
        # Load scene
        scene = load_scene_safely(blend_path)
        setup_camera_bounds(scene)
        
        # Apply settings
        scene.frame_start = start_frame
        scene.frame_end = end_frame
        if 'fps' in settings:
            scene.render.fps = settings['fps']
        if 'resolution_x' in settings:
            scene.render.resolution_x = settings['resolution_x']
        if 'resolution_y' in settings:
            scene.render.resolution_y = settings['resolution_y']
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Render frames
        for frame in range(start_frame, end_frame + 1):
            frame_path = output_dir / f"frame_{frame:04d}.png"
            
            # Skip existing valid frames
            if frame_path.exists() and frame_path.stat().st_size > 0:
                log(f"Process {process_id}: Skipping frame {frame}")
                continue
                
            log(f"Process {process_id}: Rendering frame {frame}")
            
            # Get fresh depsgraph for each frame
            depsgraph = bpy.context.evaluated_depsgraph_get()
            
            # Render with retries
            for attempt in range(MAX_RETRIES):
                try:
                    if render_frame_direct(scene, frame, frame_path, depsgraph):
                        log(f"Process {process_id}: Rendered frame {frame}")
                        break
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise
                    log(f"Attempt {attempt + 1} failed: {str(e)}", "WARNING")
                    time.sleep(1)  # Wait before retry
        
        return True
        
    except Exception as e:
        log(f"Render worker failed: {str(e)}", "ERROR")
        return False

def assemble_video(
    frame_pattern: str,
    output_path: Path,
    fps: int,
    process_id: int = 0
) -> bool:
    """Assemble frames into a video using ffmpeg."""
    try:
        log(f"Process {process_id}: Assembling video with ffmpeg")
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-y',
            '-framerate', str(fps),
            '-i', str(frame_pattern),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', str(fps),
            '-crf', '18',
            '-preset', 'slow',
            '-movflags', '+faststart',
            '-loglevel', 'error',
            '-stats',
            str(output_path)
        ]
        
        log(f"Running: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log(f"ffmpeg: {output.strip()}", "DEBUG")
        
        if process.returncode != 0:
            raise RenderError(f"FFmpeg failed with code {process.returncode}")
            
        # Verify output
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RenderError("FFmpeg did not produce any output")
            
        return True
        
    except Exception as e:
        log(f"Video assembly failed: {str(e)}", "ERROR")
        if output_path.exists():
            try:
                output_path.unlink()
            except:
                pass
        return False

def main():
    if '--' not in sys.argv:
        log("Error: No arguments provided", "ERROR")
        sys.exit(1)
        
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) < 2:
        log("Error: Missing required arguments: <settings_path> <blend_path> <output_dir> [start_frame] [end_frame]", "ERROR")
        sys.exit(1)
        
    settings_path = Path(args[0])
    blend_path = Path(args[1])
    output_dir = Path(args[2])
    start_frame = int(args[3]) if len(args) > 3 else None
    end_frame = int(args[4]) if len(args) > 4 else None
    
    try:
        # Load settings
        settings = {}
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        
        # Set up process management
        process_id = os.getpid()
        atexit.register(lambda: log(f"Process {process_id} exiting", "INFO"))
        
        # Check disk space
        if not check_disk_space(output_dir):
            raise RenderError(f"Insufficient disk space (need at least {MIN_DISK_SPACE_MB}MB free)")
        
        # Load scene to get frame range if not specified
        if start_frame is None or end_frame is None:
            scene = load_scene_safely(blend_path)
            start_frame = start_frame if start_frame is not None else scene.frame_start
            end_frame = end_frame if end_frame is not None else scene.frame_end
        
        # Render animation
        success = render_animation_worker(
            blend_path,
            output_dir,
            settings,
            start_frame,
            end_frame,
            process_id
        )
        
        # Assemble video if this is the main process and we rendered the full range
        if start_frame == 1 and end_frame == scene.frame_end:
            frame_pattern = str(output_dir / "frame_%04d.png")
            video_path = output_dir.parent / f"{blend_path.stem}.mp4"
            if not assemble_video(frame_pattern, video_path, settings.get('fps', 30), process_id):
                raise RenderError("Video assembly failed")
        
        if not success:
            log("Render failed", "ERROR")
            sys.exit(1)
            
        log("Render completed successfully", "SUCCESS")
        sys.exit(0)
            
    except Exception as e:
        log(f"Fatal error: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()