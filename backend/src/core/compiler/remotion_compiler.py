"""
Remotion Compiler: Converts Scene JSON to Remotion React code.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RemotionCompiler:
    """Compiles Scene JSON into Remotion React components."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"

    def compile(self, scene_json: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """
        Compile SceneJSON into Remotion project structure.

        Args:
            scene_json: Parsed scene data
            output_dir: Directory to write compiled code

        Returns:
            Dict with compilation metadata
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract timeline scenes
        timeline = scene_json.get("timeline", [])
        if not timeline:
            raise ValueError("No scenes found in timeline")

        # Get global settings
        global_settings = scene_json.get("settings", {})

        # Compile each scene
        compiled_scenes = []
        for scene_data in timeline:
            scene_result = self._compile_scene(scene_data, global_settings, output_dir)
            compiled_scenes.append(scene_result)

        # Generate main composition
        main_file = self._generate_main_composition(
            compiled_scenes, global_settings, output_dir
        )

        # Generate package.json and config
        self._generate_project_files(global_settings, output_dir)

        return {
            "status": "compiled",
            "main_file": str(main_file),
            "scenes": compiled_scenes,
            "engines": ["remotion"],
            "build_command": "npm run build",
        }

    def _compile_scene(
        self,
        scene_data: Dict[str, Any],
        global_settings: Dict[str, Any],
        output_dir: Path,
    ) -> Dict[str, Any]:
        """Compile individual scene data into React component."""
        scene_type = scene_data.get("type", "text")
        content = scene_data.get("content", {})
        animations = scene_data.get("animations", [])
        style = scene_data.get("style", "modern")

        # Generate component based on scene type
        if scene_type == "text":
            component_code = self._generate_text_scene(
                content, animations, global_settings
            )
        elif scene_type == "animation":
            component_code = self._generate_animation_scene(
                content, animations, global_settings
            )
        else:
            component_code = self._generate_default_scene(
                content, animations, global_settings
            )

        # Write component file
        component_name = f"{scene_data.get('id', 'Scene')}.tsx"
        component_path = output_dir / "src" / component_name
        component_path.parent.mkdir(parents=True, exist_ok=True)

        with open(component_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        return {
            "scene_id": scene_data.get("id"),
            "component_name": component_name,
            "component_path": str(component_path),
            "scene_type": scene_type,
            "duration": scene_data.get("duration", 5.0),
        }

    def _generate_text_scene(
        self,
        content: Dict[str, Any],
        animations: List[Dict[str, Any]],
        settings: Dict[str, Any],
    ) -> str:
        """Generate Remotion component for text scenes."""
        text = content.get("text", "Generated Text")
        duration_frames = int(settings.get("duration", 5.0) * settings.get("fps", 30))

        # Get colors
        colors = settings.get("colors", ["blue"])
        primary_color = colors[0] if colors else "blue"

        color_map = {
            "blue": "#3B82F6",
            "green": "#10B981",
            "red": "#EF4444",
            "purple": "#8B5CF6",
            "orange": "#F59E0B",
            "yellow": "#EAB308",
            "black": "#000000",
            "white": "#FFFFFF",
        }

        bg_color = color_map.get(primary_color, "#3B82F6")
        text_color = (
            "#FFFFFF"
            if primary_color in ["blue", "green", "red", "purple", "black"]
            else "#000000"
        )

        # Generate animations
        animations_code = self._generate_animation_code(animations, duration_frames)

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame, Audio }} from 'remotion';

export const TextScene: React.FC = () => {{
  const frame = useCurrentFrame();

  // Animation logic
  {animations_code}

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${bg_color}80 0%, ${self._adjust_color(bg_color, -20)} 100%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      <div
        style={{
          ...animatedStyle,
          fontSize: '4rem',
          fontWeight: 'bold',
          color: '{text_color}',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          maxWidth: '80%',
          lineHeight: '1.2',
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
}};
"""

        return component_code

    def _generate_animation_scene(
        self,
        content: Dict[str, Any],
        animations: List[Dict[str, Any]],
        settings: Dict[str, Any],
    ) -> str:
        """Generate component for custom animations."""
        description = content.get("description", "Animation Scene")
        duration_frames = int(settings.get("duration", 5.0) * settings.get("fps", 30))

        animations_code = self._generate_animation_code(animations, duration_frames)

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, useCurrentFrame }} from 'remotion';

export const AnimationScene: React.FC = () => {{
  const frame = useCurrentFrame();

  // Animation logic
  {animations_code}

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          ...animatedStyle,
          padding: '2rem',
          borderRadius: '1rem',
          background: 'rgba(255,255,255,0.1)',
          border: '2px solid rgba(255,255,255,0.2)',
        }}
      >
        <h1 style={{ color: 'white', fontSize: '3rem', margin: 0 }}>
          Animation Scene
        </h1>
        <p style={{ color: 'rgba(255,255,255,0.8)', margin: '1rem 0 0 0' }}>
          {description}
        </p>
      </div>
    </AbsoluteFill>
  );
}};
"""

        return component_code

    def _generate_default_scene(
        self,
        content: Dict[str, Any],
        animations: List[Dict[str, Any]],
        settings: Dict[str, Any],
    ) -> str:
        """Generate default scene component."""
        description = content.get("description", "Default Scene")

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, useCurrentFrame }} from 'remotion';

export const DefaultScene: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          fontSize: '4rem',
          fontWeight: 'bold',
          color: 'white',
          textAlign: 'center',
          textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
        }}
      >
        {description}
      </div>
    </AbsoluteFill>
  );
}};
"""

        return component_code

    def _generate_animation_code(
        self, animations: List[Dict[str, Any]], total_frames: int
    ) -> str:
        """Generate animation interpolation code."""
        codes = []

        for i, anim in enumerate(animations):
            anim_type = anim.get("type", "fade")

            if anim_type == "fade":
                direction = anim.get("direction", "in")
                start_opacity = 0.0 if direction == "in" else 1.0
                end_opacity = 1.0 if direction == "in" else 0.0

                codes.append(
                    f"""
  const opacity{i} = interpolate(
    frame,
    [0, {int(total_frames * 0.2)}, {int(total_frames * 0.8)}, {total_frames}],
    [{start_opacity}, {end_opacity}, {end_opacity}, {end_opacity}],
    {{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }}
  );"""
                )

            elif anim_type == "scale":
                start_scale = anim.get("start_scale", 0.8)
                end_scale = anim.get("end_scale", 1.2)

                codes.append(
                    f"""
  const scale{i} = interpolate(
    frame,
    [0, {int(total_frames * 0.5)}],
    [{start_scale}, {end_scale}],
    {{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }}
  );"""
                )

        # Combine into animatedStyle
        style_parts = []

        # Apply fade if available
        fade_animations = [anim for anim in animations if anim.get("type") == "fade"]
        if fade_animations:
            style_parts.append("opacity: opacity0")

        # Apply scale if available
        scale_animations = [anim for anim in animations if anim.get("type") == "scale"]
        if scale_animations:
            style_parts.append("transform: `scale(${scale0})`")

        animated_style = ""
        if style_parts:
            animated_style = f"""
  const animatedStyle = {{
    {', '.join(style_parts)}
  }};"""
        else:
            animated_style = """
  const animatedStyle = {};"""

        return "\n".join(codes) + animated_style

    def _generate_main_composition(
        self, scenes: List[Dict[str, Any]], settings: Dict[str, Any], output_dir: Path
    ) -> Path:
        """Generate main Remotion composition file."""
        duration_frames = int(settings.get("duration", 5.0) * settings.get("fps", 30))
        width, height = self._parse_resolution(settings.get("resolution", "1920x1080"))

        composition_code = f"""import {{ Composition }} from 'remotion';
import {{ TextScene }} from './TextScene';

// Note: Import additional scenes as needed
// import {{ AnimationScene }} from './AnimationScene';

export const RemotionVideo: React.FC = () => {{
  return (
    <>
      <Composition
        id="MainComposition"
        component={TextScene}
        durationInFrames={duration_frames}
        fps={settings.get("fps", 30)}
        width={width}
        height={height}
      />
    </>
  );
}};
"""

        main_file = output_dir / "src" / "Composition.tsx"
        main_file.parent.mkdir(parents=True, exist_ok=True)

        with open(main_file, "w", encoding="utf-8") as f:
            f.write(composition_code)

        return main_file

    def _generate_project_files(self, settings: Dict[str, Any], output_dir: Path):
        """Generate Remotion project configuration files."""
        # package.json
        package_json = {
            "name": "omnivid-remotion-project",
            "version": "1.0.0",
            "description": "Generated Remotion project for OmniVid",
            "scripts": {
                "dev": "remotion studio",
                "build": "remotion render MainComposition out/video.mp4",
                "render": "remotion render MainComposition out/video.mp4",
            },
            "dependencies": {
                "@remotion/bundler": "^4.0.0",
                "@remotion/cli": "^4.0.0",
                "@remotion/renderer": "^4.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
            },
        }

        with open(output_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)

        # remotion.config.ts
        config_code = """import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setPixelFormat('yuv420p');

export default Config;
"""

        with open(output_dir / "remotion.config.ts", "w", encoding="utf-8") as f:
            f.write(config_code)

    def _adjust_color(self, hex_color: str, amount: int) -> str:
        """Lighten or darken a hex color."""
        if not hex_color.startswith("#"):
            return hex_color

        # Simple color adjustment (basic implementation)
        if amount > 0:
            return hex_color  # Lighten - for now just return original
        else:
            return hex_color  # Darken - for now just return original

    def _parse_resolution(self, resolution: str) -> tuple[int, int]:
        """Parse resolution string like '1920x1080'."""
        try:
            width, height = resolution.split("x")
            return int(width), int(height)
        except:
            return 1920, 1080  # Default


# Compiler instance
remotion_compiler = RemotionCompiler()
