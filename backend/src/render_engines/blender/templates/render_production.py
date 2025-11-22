"""
Production-Grade Frame-by-Frame Renderer with Retries and Validation
Implements all guardrails for CI reliability.
"""

import bpy
import json
import sys
import os
import hashlib
import time
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class RenderMetrics:
    """Tracks detailed render performance metrics."""
    def __init__(self):
        self.start_time = time.time()
        self.frame_times: List[float] = []
        self.retry_count = 0
        self.cold_restart_count = 0
        self.frames_rendered = 0
        self.frames_failed = 0
        self.memory_peak = 0
        self.gpu_memory_peak = 0

    def record_frame_time(self, frame_time: float):
        self.frame_times.append(frame_time)

    def to_dict(self) -> Dict:
        return {
            'total_duration': time.time() - self.start_time,
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
            'min_frame_time': min(self.frame_times) if self.frame_times else 0,
            'max_frame_time': max(self.frame_times) if self.frame_times else 0,
            'retry_count': self.retry_count,
            'cold_restart_count': self.cold_restart_count,
            'frames_rendered': self.frames_rendered,
            'frames_failed': self.frames_failed,
            'render_fps': len(self.frame_times) / (time.time() - self.start_time) if self.frame_times else 0,
            'memory_peak_mb': self.memory_peak / (1024*1024) if self.memory_peak else 0,
            'gpu_memory_peak_mb': self.gpu_memory_peak / (1024*1024) if self.gpu_memory_peak else 0
        }


class ProductionRenderer:
    """Production renderer with comprehensive error handling and retries."""

    def __init__(self, settings: Dict, metrics: RenderMetrics):
        self.settings = settings
        self.metrics = metrics
        self.scene: Optional[bpy.types.Scene] = None
        self.frame_range: Tuple[int, int] = (1, 1)
        self.output_dir: Path = Path(settings.get('temp_dir', '/tmp'))
        self.frame_retries: Dict[int, int] = {}
        self.max_frame_retries = 3
        self.max_cold_restarts = 2

    def setup_render_environment(self):
        """Configure Blender for deterministic, production rendering."""
        scene = bpy.context.scene
        self.scene = scene

        # Disable all non-deterministic features
        scene.render.use_motion_blur = False
        scene.render.use_border = False
        scene.render.use_compositing = True  # But configure deterministically

        # Set deterministic seeds
        try:
            bpy.context.scene.cycles.seed = hash(str(self.settings.get('job_id', 'default'))) % 2147483647
        except AttributeError:
            pass  # Cycles not available

        # Disable auto-save and other UI features
        bpy.context.preferences.filepaths.use_auto_save_temporary_files = False

        # Optimize for headless performance
        scene.render.use_persistent_data = True
        scene.render.use_file_extension = True

        # Configure output
        scene.render.filepath = str(self.output_dir / "frame_")
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.use_overwrite = True

    def validate_manifest(self, manifest_path: Path) -> bool:
        """Validate manifest hash and scene integrity."""
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            # Verify validation hash
            expected_hash = manifest.get('validation_hash', '')
            settings = manifest.get('settings', {})
            timestamp = manifest.get('timestamp', '')
            blender_version = manifest.get('blender_version', '')

            hash_data = {
                'settings': settings,
                'timestamp': timestamp,
                'blender_version': blender_version
            }
            hash_string = json.dumps(hash_data, sort_keys=True, default=str)
            computed_hash = hashlib.sha256(hash_string.encode()).hexdigest()

            if computed_hash != expected_hash:
                print(f"ERROR: Manifest hash mismatch! Expected {expected_hash}, got {computed_hash}")
                return False

            # Check Blender version compatibility
            current_version = bpy.app.version_string
            if current_version != blender_version:
                print(f"WARNING: Blender version mismatch. Scene: {blender_version}, Current: {current_version}")

            # Validate expected frame range
            expected_range = manifest.get('expected_outputs', {}).get('frame_range', (1, 1))
            actual_range = (self.scene.frame_start, self.scene.frame_end)

            if actual_range != tuple(expected_range):
                print(f"ERROR: Frame range mismatch. Expected {expected_range}, got {actual_range}")
                return False

            print(f"Manifest validation successful. Hash: {expected_hash[:8]}...")
            return True

        except Exception as e:
            print(f"Manifest validation failed: {e}")
            return False

    def guardrails_check(self, scene: bpy.types.Scene) -> bool:
        """Comprehensive pre-render validation."""
        errors = []

        # Camera validation
        if not scene.camera:
            errors.append("No active camera in scene")

        if scene.camera and not scene.camera.data:
            errors.append("Camera has no camera data")

        # Frame range validation
        if scene.frame_end <= scene.frame_start:
            errors.append(f"Invalid frame range: {scene.frame_start}-{scene.frame_end}")

        # Resolution validation
        expected_res = self.settings.get('resolution', (1920, 1080))
        if (scene.render.resolution_x, scene.render.resolution_y) != tuple(expected_res):
            errors.append(f"Resolution mismatch. Expected {expected_res}, got {(scene.render.resolution_x, scene.render.resolution_y)}")

        # Object validation - ensure there are renderable objects
        renderable_objects = [obj for obj in scene.objects
                            if obj.visible_get() and obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}]
        if not renderable_objects:
            errors.append("No visible renderable objects in scene")

        # Material validation
        missing_textures = []
        for obj in renderable_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if hasattr(node, 'image') and node.image:
                                if not node.image.filepath or not os.path.exists(bpy.path.abspath(node.image.filepath)):
                                    missing_textures.append(node.image.filepath or f"unnamed_texture_{node.name}")

        if missing_textures:
            errors.append(f"Missing textures: {', '.join(missing_textures[:3])}")
            if len(missing_textures) > 3:
                errors[-1] += f" (+{len(missing_textures) - 3} more)"

        # Collections validation
        if not scene.collection.all_objects:
            errors.append("Scene collection is empty")

        # Render engine validation
        if scene.render.engine not in ['BLENDER_EEVEE', 'CYCLES']:
            errors.append(f"Unsupported render engine: {scene.render.engine}")

        if errors:
            print("PRE-RENDER VALIDATION FAILED:")
            for error in errors:
                print(f"  ERROR: {error}")
            return False

        print("Pre-render validation passed ✓")
        return True

    def render_frame_with_retry(self, frame: int) -> bool:
        """Render a single frame with retry logic and atomic writes."""
        frame_dir = self.output_dir / "frames"
        frame_dir.mkdir(exist_ok=True)

        frame_path = frame_dir / f"{frame:04d}.png"
        temp_frame_path = frame_dir / f"{frame:04d}.png.tmp"
        ok_file_path = frame_dir / f"{frame:04d}.ok"

        for attempt in range(self.max_frame_retries + 1):
            try:
                frame_start = time.time()

                # Clean up any previous failed attempts
                if temp_frame_path.exists():
                    temp_frame_path.unlink()
                if ok_file_path.exists():
                    ok_file_path.unlink()

                # Set frame
                self.scene.frame_set(frame)

                # Update depsgraph for this frame
                depsgraph = bpy.context.evaluated_depsgraph_get()
                depsgraph.update()

                # Render to temporary file first (atomic write)
                original_filepath = self.scene.render.filepath
                self.scene.render.filepath = str(temp_frame_path)

                # Render frame using direct API (not INVOKE_DEFAULT)
                if hasattr(bpy.ops.render, 'render') and hasattr(bpy.ops.render.render, 'animation'):
                    # Direct render without operator
                    result = bpy.ops.render.render(write_still=True, scene=self.scene.name)
                    success = result == {'FINISHED'}
                else:
                    # Fallback using scene.render.filepath
                    self.scene.render.filepath = str(temp_frame_path)
                    result = bpy.ops.render.render(animation=False, write_still=True)
                    success = result == {'FINISHED'}

                # Restore original filepath
                self.scene.render.filepath = original_filepath

                if success and temp_frame_path.exists() and temp_frame_path.stat().st_size > 0:
                    # Verify PNG header (basic validation)
                    with open(temp_frame_path, 'rb') as f:
                        header = f.read(8)
                        if header.startswith(b'\x89PNG'):
                            # Atomic move to final location
                            temp_frame_path.replace(frame_path)

                            # Write .ok file to indicate successful completion
                            ok_file_path.write_text(f"completed_at={int(time.time())}\nattempt={attempt + 1}\nsize={frame_path.stat().st_size}")

                            frame_time = time.time() - frame_start
                            self.metrics.record_frame_time(frame_time)
                            self.metrics.frames_rendered += 1
                            print(f"Frame {frame} rendered successfully ({frame_time:.2f}s)")
                            return True
                        else:
                            print(f"Invalid PNG header for frame {frame}")
                            if temp_frame_path.exists():
                                temp_frame_path.unlink()

                # Cleanup failed output
                if temp_frame_path.exists():
                    temp_frame_path.unlink()

            except Exception as e:
                print(f"Frame {frame} attempt {attempt + 1} failed: {e}")
                # Clean up any partial writes
                for path in [temp_frame_path, frame_path]:
                    if path.exists():
                        try:
                            path.unlink()
                        except:
                            pass

            if attempt < self.max_frame_retries:
                print(f"Retrying frame {frame} (attempt {attempt + 2}/{self.max_frame_retries + 1})")
                self.metrics.retry_count += 1
                time.sleep(1)  # Brief delay before retry


            if not failed_frames:
                print("All frames rendered successfully!")
                return True

            print(f"Frames failed after restart {restart_attempt}: {failed_frames}")

            if restart_attempt == self.max_cold_restarts:
                break

            # Prepare for cold restart - would reload the .blend file fresh
            print("Initiating cold restart...")

        print(f"Render failed permanently. Failed frames: {failed_frames}")
        return False

    def validate_rendered_frames(self) -> bool:
        """Validate all rendered frames exist and are valid."""
        start_frame, end_frame = self.frame_range
        expected_frames = end_frame - start_frame + 1

        frames_dir = self.output_dir / "frame_"
        frame_pattern = "frame_*.png"

        actual_frames = []
        invalid_frames = []

        for frame in range(start_frame, end_frame + 1):
            frame_path = frames_dir / f"{frame:04d}.png"
            if not frame_path.exists():
                print(f"Missing frame: {frame}")
                return False

            if frame_path.stat().st_size == 0:
                print(f"Zero-size frame: {frame}")
                invalid_frames.append(frame)
                continue

            # Check PNG validity
            try:
                with open(frame_path, 'rb') as f:
                    header = f.read(8)
                    if not header.startswith(b'\x89PNG'):
                        invalid_frames.append(frame)
                        continue
            except Exception as e:
                print(f"Error reading frame {frame}: {e}")
                invalid_frames.append(frame)
                continue

            actual_frames.append(frame)

        if invalid_frames:
            print(f"Invalid frames found: {invalid_frames}")
            return False

        if len(actual_frames) != expected_frames:
            print(f"Frame count mismatch. Expected {expected_frames}, got {len(actual_frames)}")
            return False

        print(f"Frame validation successful: {len(actual_frames)} frames ✓")
        return True

    def assemble_video_ffmpeg(self, output_path: str) -> bool:
        """Assemble frames into video using ffmpeg with comprehensive validation."""
        try:
            frames_pattern = str(self.output_dir / "frame_" / "frame_%04d.png")
            fps = self.settings.get('fps', 30)

            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', frames_pattern,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                '-crf', '18',
                '-movflags', '+faststart',
                '-loglevel', 'info',
                output_path
            ]

            print(f"Assembling video with ffmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                print(f"FFMPEG failed with code {result.returncode}")
                print(f"STDERR: {result.stderr}")
                return False

            # Validate output
            output_file = Path(output_path)
            if not output_file.exists():
                print("FFMPEG produced no output file")
                return False

            if output_file.stat().st_size == 0:
                print("FFMPEG produced zero-size output")
                return False

            # Basic MP4 validation - check for MP4 header
            with open(output_file, 'rb') as f:
                header = f.read(12)
                if not header.startswith(b'\x00\x00\x00 ftypmp4'):
                    print("Output is not a valid MP4 file")
                    return False

            duration_frames = self.frame_range[1] - self.frame_range[0] + 1
            expected_duration_sec = duration_frames / fps

            print(f"Video assembly successful: {output_file.stat().st_size} bytes, ~{expected_duration_sec:.1f}s")
            return True

        except subprocess.TimeoutExpired:
            print("FFMPEG assembly timeout")
            return False
        except Exception as e:
            print(f"FFMPEG assembly error: {e}")
            return False


def main():
    """Main production render entry point."""
    try:
        # Robust argument parsing compatible with Blender script execution
        args = sys.argv

        # Find script arguments - handle both direct execution and Blender calls
        script_args = []
        found_separator = False

        for i, arg in enumerate(args):
            if arg == '--':
                script_args = args[i+1:]  # Everything after --
                found_separator = True
                break

        if not found_separator:
            # No -- separator, handle different invocation patterns
            # Blender might call: blender --background --python render_production.py settings.json blend.mp4 output.mp4
            i = 0
            # Skip blender executable if present
            if len(args) > 0 and 'blender' in args[0]:
                i += 1
            # Skip blender flags
            while i < len(args) and args[i].startswith('-'):
                i += 1
            # Skip script name
            if i < len(args):
                i += 1
            script_args = args[i:]

        if len(script_args) < 3:
            print("Usage: render_production.py <settings.json> <blend_file> <output_path>", file=sys.stderr)
            sys.exit(1)

        settings_path = script_args[0]
        blend_path = script_args[1]
        output_path = script_args[2]

        # Load settings
        with open(settings_path, 'r') as f:
            settings = json.load(f)

        print(f"Starting production render for job: {settings.get('job_id', 'unknown')}")
        print(f"Scene: {blend_path}")
        print(f"Output: {output_path}")

        # Load blend file
        print(f"Loading scene: {blend_path}")
        bpy.ops.wm.open_mainfile(filepath=blend_path, load_ui=False)

        if not bpy.context.scene:
            print("ERROR: No scene loaded", file=sys.stderr)
            sys.exit(1)

        # Initialize renderer and metrics
        metrics = RenderMetrics()
        renderer = ProductionRenderer(settings, metrics)

        # Extract frame range from scene
        scene = bpy.context.scene
        renderer.frame_range = (scene.frame_start, scene.frame_end)

        # Validate manifest
        manifest_path = Path(blend_path).parent / f"{Path(blend_path).stem}_manifest.json"
        if not manifest_path.exists():
            print("ERROR: No manifest found", file=sys.stderr)
            sys.exit(1)

        if not renderer.validate_manifest(manifest_path):
            print("ERROR: Manifest validation failed", file=sys.stderr)
            sys.exit(1)

        # Setup render environment
        renderer.setup_render_environment()

        # Pre-render guardrails check
        if not renderer.guardrails_check(scene):
            print("ERROR: Pre-render validation failed", file=sys.stderr)
            sys.exit(1)

        # Execute render with cold restart logic
        render_success = renderer.render_with_cold_restart_logic()

        if not render_success:
            print("ERROR: Render failed after all retries", file=sys.stderr)
            sys.exit(1)

        # Validate rendered frames
        if not renderer.validate_rendered_frames():
            print("ERROR: Frame validation failed", file=sys.stderr)
            sys.exit(1)

        # Assemble final video
        if not renderer.assemble_video_ffmpeg(output_path):
            print("ERROR: Video assembly failed", file=sys.stderr)
            sys.exit(1)

        # Final metrics output
        final_metrics = metrics.to_dict()
        print(f"Render completed successfully!")
        print(f"Frames: {metrics.frames_rendered}/{metrics.frames_rendered + metrics.frames_failed}")
        print(f"Time: {final_metrics['total_duration']:.1f}s")
        print(f"FPS: {final_metrics['render_fps']:.1f}")
        print(f"Retries: {metrics.retry_count}")
        print(f"Cold restarts: {metrics.cold_restart_count}")

        # Save metrics to manifest update
        metrics_path = Path(output_path).parent / f"{Path(output_path).stem}_metrics.json"
        try:
            with open(metrics_path, 'w') as f:
                json.dump(final_metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metrics: {e}")

        print(f"Final output: {output_path}")
        sys.exit(0)

    except Exception as e:
        print(f"Critical render error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
