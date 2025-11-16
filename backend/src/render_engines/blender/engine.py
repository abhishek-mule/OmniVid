"""
Blender render engine implementation.
"""
import os
import bpy
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from .base import RenderEngine, RenderEngineType, RenderResult, RenderStatus

logger = logging.getLogger(__name__)

class BlenderRenderEngine(RenderEngine):
    """Blender render engine for 3D animation and video creation."""
    
    def __init__(self):
        super().__init__("Blender", ["mp4", "avi", "mov", "mkv"])
        self.blender_path = None
        self.temp_dir = None
    
    def initialize(self) -> bool:
        """Initialize Blender and check if it's available."""
        try:
            # Check if Blender is available in system PATH
            import shutil
            self.blender_path = shutil.which("blender")
            
            if not self.blender_path:
                # Check common installation paths
                common_paths = [
                    "/usr/bin/blender",
                    "/usr/local/bin/blender",
                    "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
                    "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        self.blender_path = path
                        break
            
            if self.blender_path:
                # Get Blender version
                result = subprocess.run(
                    [self.blender_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.version = result.stdout.strip().split('\n')[0]
                    self.is_available = True
                    logger.info(f"Blender initialized successfully: {self.version}")
                    return True
            
            logger.warning("Blender not found or not accessible")
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Blender: {str(e)}")
            return False
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate Blender-specific settings."""
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
            
            # Check render engine type (cycles or eevee)
            render_engine = settings.get("render_engine", "eevee")
            if render_engine not in ["eevee", "cycles"]:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Settings validation failed: {str(e)}")
            return False
    
    def create_scene(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Create a Blender scene based on prompt and settings."""
        try:
            # Create temporary directory for scene files
            self.temp_dir = tempfile.mkdtemp(prefix="omnivid_blender_")
            
            # Create a basic scene script
            scene_script = self._generate_scene_script(prompt, settings)
            
            # Save scene file
            scene_path = os.path.join(self.temp_dir, "scene.blend")
            
            # Write the scene creation script
            script_path = os.path.join(self.temp_dir, "create_scene.py")
            with open(script_path, 'w') as f:
                f.write(scene_script)
            
            # Use Blender to create the scene
            result = subprocess.run([
                self.blender_path,
                "--background",
                "--python", script_path,
                "--render-anim",
                "--output", os.path.join(self.temp_dir, "render_"),
                "--render-frame", "1"  # Render first frame to create scene file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Return the script path which will be used for rendering
                return script_path
            else:
                logger.error(f"Failed to create scene: {result.stderr}")
                raise RuntimeError(f"Blender scene creation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error creating Blender scene: {str(e)}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise
    
    def render_video(self, scene_path: str, output_path: str, progress_callback=None) -> RenderResult:
        """Render video using Blender."""
        try:
            if progress_callback:
                progress_callback(0, RenderStatus.INITIALIZING, "Starting Blender render")
            
            # Parse settings from scene script (in a real implementation, this would be more sophisticated)
            settings = self._extract_settings_from_script(scene_path)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if progress_callback:
                progress_callback(20, RenderStatus.RENDERING, "Initializing render")
            
            # Run Blender render
            render_args = [
                self.blender_path,
                "--background",
                "--python", scene_path,
                "--render-anim",
                "--output", output_path.replace('.mp4', '_'),
                "--render-format", "MP4"
            ]
            
            # Add resolution settings
            resolution = settings.get("resolution", (1920, 1080))
            render_args.extend([
                "--render-resolution-x", str(resolution[0]),
                "--render-resolution-y", str(resolution[1])
            ])
            
            # Add frame rate
            fps = settings.get("fps", 30)
            render_args.extend(["--render-fps", str(fps)])
            
            if progress_callback:
                progress_callback(30, RenderStatus.RENDERING, "Starting render process")
            
            # Execute render
            result = subprocess.run(
                render_args,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(90, RenderStatus.POST_PROCESSING, "Post-processing")
                
                # Check if output file exists
                if not os.path.exists(output_path):
                    # Blender might have created files with different names
                    base_path = output_path.replace('.mp4', '_0001.mp4')
                    if os.path.exists(base_path):
                        shutil.move(base_path, output_path)
                
                if os.path.exists(output_path):
                    if progress_callback:
                        progress_callback(100, RenderStatus.COMPLETED, "Render completed")
                    
                    return RenderResult(
                        success=True,
                        video_url=output_path,
                        duration=settings.get("duration", 10.0),
                        resolution=settings.get("resolution", (1920, 1080)),
                        metadata={
                            "render_engine": "blender",
                            "blender_version": self.version,
                            "settings": settings
                        }
                    )
                else:
                    raise RuntimeError("Output file was not created")
            else:
                error_msg = f"Blender render failed: {result.stderr}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(0, RenderStatus.FAILED, error_msg)
                
                return RenderResult(
                    success=False,
                    error_message=error_msg,
                    metadata={"stderr": result.stderr, "stdout": result.stdout}
                )
                
        except subprocess.TimeoutExpired:
            error_msg = "Blender render timed out"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(0, RenderStatus.FAILED, error_msg)
            return RenderResult(success=False, error_message=error_msg)
            
        except Exception as e:
            error_msg = f"Blender render error: {str(e)}"
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
            logger.error(f"Failed to cleanup Blender temp files: {str(e)}")
            return False
    
    def _generate_scene_script(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Generate Blender Python script for scene creation."""
        script = f'''
import bpy
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create camera
bpy.ops.object.camera_add(location=(0, -5, 2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)

# Create lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -1))
plane = bpy.context.active_object
plane.name = "Ground"

# Add material to ground
mat = bpy.data.materials.new(name="GroundMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Create material nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.2, 0.3, 0.4, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

# Connect nodes
mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

plane.data.materials.append(mat)

# Parse prompt for objects to create
prompt_objects = []

# Simple object creation based on prompt keywords
if "cube" in prompt.lower():
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "PromptCube"
    prompt_objects.append(cube)

if "sphere" in prompt.lower():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 0))
    sphere = bpy.context.active_object
    sphere.name = "PromptSphere"
    prompt_objects.append(sphere)

if "cylinder" in prompt.lower():
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(-3, 0, 0))
    cylinder = bpy.context.active_object
    cylinder.name = "PromptCylinder"
    prompt_objects.append(cylinder)

# Animate objects if needed
if "animate" in prompt.lower() or "motion" in prompt.lower():
    frame_count = int({settings.get("duration", 10)} * {settings.get("fps", 30)})
    
    for obj in prompt_objects:
        # Set keyframes for animation
        bpy.context.scene.frame_set(1)
        obj.location = (obj.location[0], obj.location[1], 0)
        obj.keyframe_insert(data_path="location")
        
        bpy.context.scene.frame_set(frame_count)
        obj.location = (obj.location[0], obj.location[1], 2)
        obj.keyframe_insert(data_path="location")

# Set render settings
scene = bpy.context.scene
scene.render.engine = "{settings.get("render_engine", "eevee")}"
scene.render.resolution_x = {settings.get("resolution", (1920, 1080))[0]}
scene.render.resolution_y = {settings.get("resolution", (1920, 1080))[1]}
scene.render.fps = {settings.get("fps", 30)}

# Set animation range
scene.frame_start = 1
scene.frame_end = {int(settings.get("duration", 10) * settings.get("fps", 30))}

print("Scene created successfully")
'''
        return script
    
    def _extract_settings_from_script(self, script_path: str) -> Dict[str, Any]:
        """Extract settings from the scene script (simplified)."""
        # In a real implementation, this would parse the actual settings
        # used in the scene creation
        return {
            "resolution": (1920, 1080),
            "fps": 30,
            "duration": 10,
            "render_engine": "eevee"
        }
    
    def get_supported_resolutions(self) -> List[tuple]:
        """Get Blender-supported resolutions."""
        return [
            (3840, 2160),  # 4K
            (2560, 1440),  # 2K
            (1920, 1080),  # Full HD
            (1280, 720),   # HD
            (854, 480),    # SD
        ]
    
    def get_supported_fps(self) -> List[int]:
        """Get Blender-supported frame rates."""
        return [15, 24, 30, 60, 120]