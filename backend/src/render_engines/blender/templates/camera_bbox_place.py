# camera_bbox_place.py
# Usage (inside Blender): import this file and call place_camera_for_scene(scene.camera or new_camera, scene)
import bpy
import math
from mathutils import Vector

def _scene_world_bbox(scene):
    """Return (min, max) 3-tuples in world space for all MESH objects in scene."""
    min_v = Vector((float('inf'),)*3)
    max_v = Vector((float('-inf'),)*3)
    any_mesh = False
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        any_mesh = True
        # ensure evaluated mesh world coords
        mesh = obj.data
        for v in mesh.vertices:
            world_v = obj.matrix_world @ v.co
            for i in range(3):
                if world_v[i] < min_v[i]: min_v[i] = world_v[i]
                if world_v[i] > max_v[i]: max_v[i] = world_v[i]
    return (tuple(min_v), tuple(max_v), any_mesh)

def compute_camera_distance_for_fov(target_size, fov_rad):
    """Compute distance from camera to center so that target_size fits into fov (rad)."""
    # target_size is size along largest horizontal/vertical dimension in world units,
    # assume we want to fit it in the larger of horizontal/vertical FOV.
    return (target_size / 2.0) / math.tan(fov_rad / 2.0)

def place_camera_for_scene(camera_obj, scene, padding=1.2):
    """
    Position camera_obj (bpy.types.Object of type CAMERA) to frame all mesh objects in scene.
    padding: multiplicative factor >1 to leave margin.
    """
    # Compute bbox
    min_v, max_v, has_mesh = _scene_world_bbox(scene)
    if not has_mesh:
        # fallback: default professional placement
        camera_obj.location = Vector((0.0, -12.0, 5.0))
        camera_obj.rotation_euler = (0.523599, 0.0, 0.0)  # 30 degrees down
        camera_obj.data.clip_start = 0.1
        camera_obj.data.clip_end = 1000.0
        return True

    min_v = Vector(min_v); max_v = Vector(max_v)
    center = (min_v + max_v) * 0.5
    size = max_v - min_v
    max_size = max(size.x, size.y, size.z) * padding

    # Compute camera FOV (use camera.data.angle if set, else compute from lens & sensor)
    camdata = camera_obj.data
    if hasattr(camdata, "angle") and camdata.angle:
        # Blender camera angle is horizontal FOV in radians for perspective
        fov = camdata.angle
    else:
        # approximate horizontal FOV from lens & sensor_width
        sensor = getattr(camdata, "sensor_width", 36.0)
        lens = getattr(camdata, "lens", 50.0)
        fov = 2.0 * math.atan(sensor / (2.0 * lens))

    distance = compute_camera_distance_for_fov(max_size, fov)
    # Position camera along negative Y axis looking toward center (you can change axis)
    cam_loc = Vector((center.x, center.y - distance, center.z + distance * 0.18))
    camera_obj.location = cam_loc
    # Point the camera at center:
    direction = center - camera_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')  # camera looks -Z
    camera_obj.rotation_euler = rot_quat.to_euler()
    # Adjust clip planes
    camdata.clip_start = max(0.01, distance * 0.001)
    camdata.clip_end = distance * 50.0
    return True

# Example usage when running inside Blender:
# import camera_bbox_place
# if not bpy.context.scene.camera:
#     cam = bpy.data.objects.new('AutoCam', bpy.data.cameras.new('AutoCamData'))
#     bpy.context.collection.objects.link(cam)
#     bpy.context.scene.camera = cam
# camera_bbox_place.place_camera_for_scene(bpy.context.scene.camera, bpy.context.scene)
