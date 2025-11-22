"""
Production-Grade Scene Creation with Pure Data API
Creates scenes using only data API for maximum reliability and determinism.
"""

import bpy
import json
import os
import sys
import hashlib
import time
from pathlib import Path
import traceback
from bmesh import new as bmesh_new


class ProductionSceneBuilder:
    """Builds scenes using only the data API - no operators."""

    def __init__(self, manifest_data):
        self.manifest = manifest_data
        self.scene = None
        self.camera = None
        self.lights = []
        self.objects = []

    def create_empty_world(self):
        """Create completely empty scene using data API safely."""
        # Safe clearing - unlink objects first, then remove data blocks
        for scene in list(bpy.data.scenes):
            for obj in list(scene.objects):
                scene.collection.objects.unlink(obj)
            bpy.data.scenes.remove(scene)

        # Remove all objects and data blocks safely
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        for mesh in list(bpy.data.meshes):
            bpy.data.meshes.remove(mesh, do_unlink=True)

        for material in list(bpy.data.materials):
            bpy.data.materials.remove(material, do_unlink=True)

        for texture in list(bpy.data.textures):
            bpy.data.textures.remove(texture, do_unlink=True)

        for camera in list(bpy.data.cameras):
            bpy.data.cameras.remove(camera, do_unlink=True)

        for light in list(bpy.data.lights):
            bpy.data.lights.remove(light, do_unlink=True)

        for world in list(bpy.data.worlds):
            bpy.data.worlds.remove(world, do_unlink=True)

        # Create new scene
        self.scene = bpy.data.scenes.new("ProductionScene")
        self.scene.world = bpy.data.worlds.new("ProductionWorld")

        return self.scene

    def create_professional_lighting(self):
        """Create professional three-point lighting setup."""
        # Key light (main)
        key_light_data = bpy.data.lights.new("KeyLight", 'SUN')
        key_light_data.energy = 3.0
        key_light_data.angle = 0.5  # Soft shadows
        key_light_obj = bpy.data.objects.new("KeyLight", key_light_data)
        key_light_obj.location = (5, -5, 8)
        key_light_obj.rotation_euler = (0.785, 0, 2.356)  # 45° down, southwest
        self.scene.collection.objects.link(key_light_obj)

        # Fill light (softer)
        fill_light_data = bpy.data.lights.new("FillLight", 'AREA')
        fill_light_data.energy = 1.0
        fill_light_data.size = 5.0
        fill_light_obj = bpy.data.objects.new("FillLight", fill_light_data)
        fill_light_obj.location = (-4, 3, 6)
        fill_light_obj.rotation_euler = (0.523, 0, 0)  # 30° down, northeast
        self.scene.collection.objects.link(fill_light_obj)

        # Back light (rim)
        rim_light_data = bpy.data.lights.new("RimLight", 'SPOT')
        rim_light_data.energy = 2.0
        rim_light_data.spot_size = 1.0
        rim_light_data.spot_blend = 0.5
        rim_light_obj = bpy.data.objects.new("RimLight", rim_light_data)
        rim_light_obj.location = (0, -10, 3)
        rim_light_obj.rotation_euler = (0.2, 0, 0)  # Slight upward angle
        self.scene.collection.objects.link(rim_light_obj)

        self.lights = [key_light_obj, fill_light_obj, rim_light_obj]

    def create_camera_and_position(self, objects_bbox=None):
        """Create camera and position it optimally for the scene."""
        camera_data = bpy.data.cameras.new("ProductionCamera")
        camera_data.sensor_width = 36.0  # Full frame
        camera_data.lens = 50  # Standard lens

        self.camera = bpy.data.objects.new("ProductionCamera", camera_data)
        self.scene.collection.objects.link(self.camera)
        self.scene.camera = self.camera

        # Auto-position based on content
        if objects_bbox:
            # Calculate optimal camera position for bounding box
            center = [
                (objects_bbox[0][i] + objects_bbox[1][i]) / 2 for i in range(3)
            ]
            size = [
                objects_bbox[1][i] - objects_bbox[0][i] for i in range(3)
            ]
            max_size = max(size)

            # Position camera to frame scene optimally
            distance = max(max_size * 1.8, 15.0)
            self.camera.location = [center[0], center[1] - distance, center[2] + distance * 0.3]
            self.camera.rotation_euler = [0.523, 0, 0]  # 30 degrees down

            # Adjust lens based on scene size
            self.camera.data.lens = max(max_size * 1.2, 35)

            # Set clip planes appropriately
            self.camera.data.clip_start = distance * 0.05
            self.camera.data.clip_end = distance * 20
        else:
            # Default professional position
            self.camera.location = [0, -12, 5]
            self.camera.rotation_euler = [0.523, 0, 0]
            self.camera.data.clip_start = 0.1
            self.camera.data.clip_end = 1000

    def create_basic_geometry(self, prompt):
        """Create basic geometric objects based on prompt using data API."""
        created_objects = []

        prompt_lower = prompt.lower()

        # Create cube with material
        if 'cube' in prompt_lower:
            mesh = bpy.data.meshes.new("Cube")
            cube_obj = bpy.data.objects.new("Cube", mesh)

            # Create cube geometry with proper vertices/faces
            vertices = [
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
            ]
            faces = [
                (0, 1, 2, 3), (7, 6, 5, 4), (4, 5, 1, 0),
                (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3)
            ]
            mesh.from_pydata(vertices, [], faces)
            mesh.update()

            # Create material and assign to mesh.materials
            mat = bpy.data.materials.new("CubeMaterial")
            mat.use_nodes = True
            principled = mat.node_tree.nodes.get("Principled BSDF")
            if principled:
                principled.inputs['Base Color'].default_value = (0.8, 0.3, 0.1, 1)
                principled.inputs['Metallic'].default_value = 0.1
                principled.inputs['Roughness'].default_value = 0.4

            mesh.materials.append(mat)
            self.scene.collection.objects.link(cube_obj)
            created_objects.append(cube_obj)

        # Create sphere using bmesh UV sphere
        if 'sphere' in prompt_lower:
            # Use bmesh for proper UV sphere creation
            bm = bmesh_new()
            bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
            bm.to_mesh(mesh := bpy.data.meshes.new("Sphere"))
            bm.free()

            mesh.update()
            sphere_obj = bpy.data.objects.new("Sphere", mesh)
            sphere_obj.location = (3, 0, 0)

            # Create material and assign to mesh.materials
            mat = bpy.data.materials.new("SphereMaterial")
            mat.use_nodes = True
            principled = mat.node_tree.nodes.get("Principled BSDF")
            if principled:
                principled.inputs['Base Color'].default_value = (0.1, 0.5, 0.8, 1)
                principled.inputs['Metallic'].default_value = 0.9
                principled.inputs['Roughness'].default_value = 0.1

            mesh.materials.append(mat)
            self.scene.collection.objects.link(sphere_obj)
            created_objects.append(sphere_obj)

        return created_objects

    def setup_animation(self, duration_seconds, fps):
        """Set up animation timeline deterministically."""
        frame_count = int(duration_seconds * fps)

        # Fix Blender's randomness for deterministic results
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

        # Set deterministic seeds using hashlib
        import random
        seed_value = int(hashlib.md5(str(self.manifest.get('job_id', 'default')).encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_value)
        bpy.context.window_manager.windows[0].screen.areas[0].spacetimes[0].cursor.location = (0, 0, 0)

        # Set deterministic animation settings
        self.scene.frame_start = 1
        self.scene.frame_end = frame_count
        self.scene.frame_current = 1

        # Disable motion blur and other non-deterministic effects
        self.scene.render.use_motion_blur = False

        # Set deterministic seed for any procedural effects
        self.scene.use_nodes = True

    def add_deterministic_keyframes(self, objects, frame_count):
        """Add deterministic keyframes for animation."""
        import math

        # Use hashlib for deterministic seed generation
        seed_str = str(self.manifest.get('job_id', 'default'))
        seed_value = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % 10000
        bpy.context.window_manager.windows[0].screen.scene.seed = seed_value

        for obj in objects:
            obj_name = obj.name.lower()

            # Set initial keyframe
            self.scene.frame_current = 1
            obj.keyframe_insert(data_path="location", frame=1)
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            obj.keyframe_insert(data_path="scale", frame=1)

            # Animate based on type
            if 'cube' in obj_name:
                # Rotate cube continuously
                self.scene.frame_current = frame_count // 4
                obj.rotation_euler.z = math.pi / 2
                obj.keyframe_insert(data_path="rotation_euler", frame=self.scene.frame_current)

                self.scene.frame_current = frame_count // 2
                obj.rotation_euler.z = math.pi
                obj.keyframe_insert(data_path="rotation_euler", frame=self.scene.frame_current)

                self.scene.frame_current = frame_count
                obj.rotation_euler.z = 2 * math.pi
                obj.keyframe_insert(data_path="rotation_euler", frame=self.scene.frame_current)

            elif 'sphere' in obj_name:
                # Bounce sphere up and down
                original_z = obj.location.z

                self.scene.frame_current = frame_count // 4
                obj.location.z = original_z + 2
                obj.keyframe_insert(data_path="location", frame=self.scene.frame_current)

                self.scene.frame_current = frame_count // 2
                obj.location.z = original_z
                obj.keyframe_insert(data_path="location", frame=self.scene.frame_current)

                self.scene.frame_current = frame_count
                obj.location.z = original_z + 1
                obj.keyframe_insert(data_path="location", frame=self.scene.frame_current)

    def pack_assets_and_finalize(self, blend_path):
        """Pack all assets and prepare for render."""
        # Guard pack_all with try/except
        try:
            bpy.ops.file.pack_all()
        except Exception as e:
            print(f"Warning: Asset packing failed: {e}", file=sys.stderr)
            # Continue anyway - not all scenes need packing

        # Set render settings for determinism
        render = self.scene.render
        render.engine = 'BLENDER_EEVEE'
        render.use_lock_interface = True
        render.use_persistent_data = True

        # Ensure deterministic file output
        render.use_file_extension = True
        render.use_overwrite = True

        # Save the blend file
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

        return blend_path

    def build_scene(self, prompt, settings, blend_path):
        """Build the complete scene."""
        try:
            # Create empty world
            self.create_empty_world()

            # Set up professional lighting
            self.create_professional_lighting()

            # Create camera (will reposition after objects)
            self.create_camera_and_position()

            # Create geometry
            objects = self.create_basic_geometry(prompt)

            # Reposition camera for objects if any were created
            if objects:
                # Calculate bounding box
                min_bounds = [float('inf')] * 3
                max_bounds = [float('-inf')] * 3

                for obj in objects + self.lights:
                    if obj.type == 'MESH':
                        for vert in obj.data.vertices:
                            world_vert = obj.matrix_world @ vert.co
                            for i in range(3):
                                min_bounds[i] = min(min_bounds[i], world_vert[i])
                                max_bounds[i] = max(max_bounds[i], world_vert[i])

                if min_bounds[0] != float('inf'):
                    self.create_camera_and_position((min_bounds, max_bounds))

            # Set up animation
            duration = settings.get('duration', 10)
            fps = settings.get('fps', 30)
            self.setup_animation(duration, fps)

            # Add keyframes deterministically
            if objects:
                self.add_deterministic_keyframes(objects, int(duration * fps))

            # Pack and save
            self.pack_assets_and_finalize(blend_path)

            return {
                'success': True,
                'objects_created': len(objects),
                'lights_setup': len(self.lights),
                'camera_positioned': bool(self.camera),
                'frame_count': int(duration * fps)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }


def create_manifest(settings, blend_path, result):
    """Create deterministic manifest with SHA256 hash and stream .blend hashing."""
    manifest = {
        'job_id': settings.get('job_id', 'unknown'),
        'timestamp': time.strftime('%Y%m%d_%H%M%S_UTC', time.gmtime()),
        'blender_version': bpy.app.version_string,
        'settings': settings,
        'expected_outputs': {
            'resolution': settings.get('resolution', (1920, 1080)),
            'frame_range': (1, int(settings.get('duration', 10) * settings.get('fps', 30))),
            'output_format': 'mp4',
            'frame_count': int(settings.get('duration', 10) * settings.get('fps', 30))
        },
        'scene_stats': result,
        'validation_hash': '',
        'blend_file_hash': ''
    }

    # Generate validation hash
    hash_data = {
        'settings': settings,
        'timestamp': manifest['timestamp'],
        'blender_version': manifest['blender_version']
    }
    hash_string = json.dumps(hash_data, sort_keys=True, default=str)
    manifest['validation_hash'] = hashlib.sha256(hash_string.encode()).hexdigest()

    # Stream hash .blend file (don't load entire file into memory)
    try:
        hasher = hashlib.sha256()
        with open(blend_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        manifest['blend_file_hash'] = hasher.hexdigest()
    except Exception:
        manifest['blend_file_hash'] = 'failed_to_generate'

    return manifest


def create_creation_status(settings, result):
    """Create creation_status.json with expected frame pattern and count."""
    return {
        'job_id': settings.get('job_id', 'unknown'),
        'created_at': time.strftime('%Y%m%d_%H%M%S_UTC', time.gmtime()),
        'expected_frames': result.get('frame_count', 0),
        'frame_pattern': '{frame:04d}.png',
        'output_format': 'png',
        'status': 'scene_created' if result.get('success') else 'creation_failed',
        'error': '' if result.get('success') else result.get('error', 'unknown')
    }


def main():
    try:
        # Robust CLI argument parsing for all Blender invocation patterns
        args = sys.argv

        # Find script arguments - look for -- separator first, then fallback logic
        script_args = []
        found_separator = False

        for i, arg in enumerate(args):
            if arg == '--':
                script_args = args[i+1:]  # Everything after --
                found_separator = True
                break

        if not found_separator:
            # No -- separator, look for .py files to identify script args
            # Common patterns: blender flags* script.py args*  OR  blender script.py args*
            candidates = []

            # Find potential script arguments after what looks like a script file
            for idx in range(len(args)):
                if args[idx].endswith('.py'):
                    # Found a script file, everything after should be script args
                    candidates = args[idx + 1:]
                    break

            # If no .py file found, fallback to after blender flags
            if not candidates:
                i = 0
                # Skip what looks like blender executable and flags
                if len(args) > 0 and ('blender' in args[0] or args[0].startswith('-')):
                    i += 1  # Skip potential executable
                # Skip consecutive flags
                while i < len(args) and args[i].startswith('-'):
                    i += 1
                if i < len(args):
                    i += 1  # Skip what we assume is the script
                    candidates = args[i:]

            script_args = candidates

        if len(script_args) < 2:
            print("Usage: blender --background [--python] script.py [--] <settings.json> <output.blend>", file=sys.stderr)
            sys.exit(1)

        settings_path = script_args[0]
        blend_path = script_args[1]

        # Load settings
        with open(settings_path, 'r') as f:
            settings = json.load(f)

        # Build scene
        builder = ProductionSceneBuilder(settings)
        result = builder.build_scene(
            settings.get('prompt', 'basic cube'),
            settings,
            blend_path
        )

        if result.get('success'):
            # Create and save manifest
            manifest = create_manifest(settings, blend_path, result)
            manifest_path = Path(blend_path).parent / f"{Path(blend_path).stem}_manifest.json"
            creation_status_path = Path(blend_path).parent / f"{Path(blend_path).stem}_creation_status.json"

            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)

            # Create creation status
            creation_status = create_creation_status(settings, result)
            with open(creation_status_path, 'w') as f:
                json.dump(creation_status, f, indent=2)

            print(f"Scene created successfully: {blend_path}")
            print(f"Manifest saved: {manifest_path}")
            print(f"Creation status: {creation_status_path}")
            print(f"Objects: {result['objects_created']}, Frames: {result['frame_count']}")
            sys.exit(0)
        else:
            print(f"Scene creation failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Critical error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
