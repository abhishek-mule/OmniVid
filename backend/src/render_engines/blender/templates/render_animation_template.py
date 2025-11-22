"""
Fully headless-safe Blender animation renderer.
No UI operators. No state resets. No INVOKE_DEFAULT.
Reliable in CI, Docker and multi-process execution.
"""

import bpy
import json
import sys
from pathlib import Path
import traceback


class RenderError(Exception):
    pass


def validate(scene):
    if not scene.camera:
        raise RenderError("Scene has no active camera")

    if scene.frame_end < scene.frame_start:
        raise RenderError(f"Invalid frame range {scene.frame_start}-{scene.frame_end}")

    if scene.render.resolution_x == 0 or scene.render.resolution_y == 0:
        raise RenderError("Invalid resolution")


def configure_output(scene, out_path: Path):
    out_path = out_path.absolute()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ext = out_path.suffix.lower()

    if ext == ".mp4":
        scene.render.filepath = str(out_path.with_suffix(""))
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.use_file_extension = True

    else:
        # Assume image sequence
        scene.render.filepath = str(out_path)
        scene.render.image_settings.file_format = "PNG"
        scene.render.use_file_extension = True

    return out_path


def render_frames(scene):
    """Robust manual render loop — never uses INVOKE_DEFAULT."""

    for frame in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()

        filepath = scene.render.filepath.replace("####", f"{frame:04d}")

        print(f"Rendering frame {frame} -> {filepath}")

        try:
            bpy.ops.render.render(animation=False, write_still=True)
        except Exception as e:
            raise RenderError(f"Render failed at frame {frame}: {e}")


def main():
    try:
        if "--" not in sys.argv:
            raise RenderError("No arguments provided")

        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) < 2:
            raise RenderError("Usage: <settings.json> <file.blend> [output_path]")

        settings_path = Path(args[0])
        blend_path = Path(args[1])
        output_path = Path(args[2]) if len(args) > 2 else None

        if not blend_path.exists():
            raise RenderError(f"Blend file not found: {blend_path}")

        if not settings_path.exists():
            raise RenderError(f"Settings file not found: {settings_path}")

        settings = json.load(open(settings_path))

        print(f"Opening file: {blend_path}")
        bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False)

        scene = bpy.context.scene
        if not scene:
            raise RenderError("No active scene after loading blend")

        validate(scene)

        if output_path:
            output_path = configure_output(scene, output_path)

        render_frames(scene)

        print("Render completed.")
        return 0

    except RenderError as e:
        print(f"Render Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
