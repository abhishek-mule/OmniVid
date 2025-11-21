"""
AI service for natural language video generation.
Converts natural language prompts into animation code for render engines.
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PromptParser:
    """Parses natural language prompts and extracts video generation parameters."""

    def __init__(self):
        self.scene_types = {
            "text": ["text", "typography", "title", "headline"],
            "math": ["equation", "formula", "graph", "function", "mathematical"],
            "animation": ["animate", "motion", "movement", "transition"],
            "web": ["ui", "interface", "component", "react", "web"],
            "3d": ["3d", "cube", "sphere", "cylinder", "object"],
        }

    def extract_scene_type(self, prompt: str) -> str:
        """Extract the primary scene type from the prompt."""
        prompt_lower = prompt.lower()

        # Check for mathematical content
        if any(keyword in prompt_lower for keyword in self.scene_types["math"]):
            return "math"

        # Check for 3D content
        if any(keyword in prompt_lower for keyword in self.scene_types["3d"]):
            return "3d"

        # Check for web/React content
        if any(keyword in prompt_lower for keyword in self.scene_types["web"]):
            return "web"

        # Check for text content
        if any(keyword in prompt_lower for keyword in self.scene_types["text"]):
            return "text"

        # Default to animation
        return "animation"

    def extract_parameters(self, prompt: str) -> Dict[str, Any]:
        """Extract rendering parameters from the prompt."""
        params = {
            "duration": self._extract_duration(prompt),
            "resolution": self._extract_resolution(prompt),
            "style": self._extract_style(prompt),
            "colors": self._extract_colors(prompt),
            "speed": self._extract_speed(prompt),
        }
        return params

    def _extract_duration(self, prompt: str) -> float:
        """Extract duration in seconds from prompt."""
        # Look for patterns like "5 seconds", "30 second", "1 minute"
        duration_match = re.search(r"(\d+)\s*(second|minute)s?", prompt.lower())
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            return value * 60 if unit == "minute" else value
        return 5.0  # Default 5 seconds

    def _extract_resolution(self, prompt: str) -> Tuple[int, int]:
        """Extract resolution from prompt."""
        if "4k" in prompt.lower() or "ultra" in prompt.lower():
            return (3840, 2160)
        elif "1080p" in prompt.lower() or "full hd" in prompt.lower():
            return (1920, 1080)
        elif "720p" in prompt.lower() or "hd" in prompt.lower():
            return (1280, 720)
        return (1920, 1080)  # Default Full HD

    def _extract_style(self, prompt: str) -> str:
        """Extract visual style from prompt."""
        if "minimal" in prompt.lower() or "clean" in prompt.lower():
            return "minimal"
        elif "vibrant" in prompt.lower() or "colorful" in prompt.lower():
            return "vibrant"
        elif "corporate" in prompt.lower() or "professional" in prompt.lower():
            return "professional"
        return "modern"

    def _extract_colors(self, prompt: str) -> List[str]:
        """Extract color preferences from prompt."""
        colors = []
        color_keywords = {
            "blue": ["blue", "navy", "azure"],
            "green": ["green", "emerald", "teal"],
            "red": ["red", "crimson", "scarlet"],
            "purple": ["purple", "violet", "lavender"],
            "orange": ["orange", "amber"],
            "yellow": ["yellow", "gold"],
            "black": ["black", "dark"],
            "white": ["white", "light"],
        }

        prompt_lower = prompt.lower()
        for color, keywords in color_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                colors.append(color)

        return colors if colors else ["blue"]  # Default blue theme

    def _extract_speed(self, prompt: str) -> str:
        """Extract animation speed from prompt."""
        if "slow" in prompt.lower():
            return "slow"
        elif "fast" in prompt.lower() or "quick" in prompt.lower():
            return "fast"
        return "medium"


class CodeGenerator:
    """Generates animation code for different render engines."""

    def __init__(self):
        self.templates = {
            "remotion": self._get_remotion_template,
            "manim": self._get_manim_template,
            "text": self._get_text_template,
        }

    def generate_code(
        self, scene_type: str, prompt: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate code for the appropriate engine based on scene type."""
        if scene_type not in self.templates:
            scene_type = "text"  # Fallback

        return self.templates[scene_type](prompt, parameters)

    def _get_remotion_template(
        self, prompt: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Remotion React component code."""
        colors = parameters.get("colors", ["blue"])
        primary_color = colors[0] if colors else "blue"
        duration = parameters.get("duration", 5.0)
        style = parameters.get("style", "modern")

        # Map colors to hex codes
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

        hex_color = color_map.get(primary_color, "#3B82F6")

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

export const Scene: React.FC = () => {{
  const frame = useCurrentFrame();

  // Animation keyframes
  const opacity = interpolate(frame, [0, 30, 120, 135], [0, 1, 1, 0], {{
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }});

  const scale = interpolate(frame, [0, 30], [0.8, 1], {{
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }});

  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
          fontSize: '4rem',
          fontWeight: 'bold',
          color: '{hex_color}',
          textAlign: 'center',
          fontFamily: 'Inter, sans-serif',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
        }}
      >
        {prompt.split(' ').slice(0, 3).join(' ')}
      </div>
    </AbsoluteFill>
  );
}};"""

        return {
            {
                "engine": "remotion",
                "code": component_code,
                "config": {
                    {
                        "durationInFrames": int(duration * 30),  # 30 fps
                        "fps": 30,
                        "width": parameters.get("resolution", (1920, 1080))[0],
                        "height": parameters.get("resolution", (1920, 1080))[1],
                    }
                },
                "output_filename": "scene.mp4",
            }
        }

    def _get_manim_template(
        self, prompt: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Manim Python code for mathematical animations."""
        colors = parameters.get("colors", ["blue"])
        primary_color = colors[0] if colors else "blue"
        duration = parameters.get("duration", 5.0)

        # Extract mathematical content from prompt
        math_content = prompt.lower()
        has_equation = "equation" in math_content or "=" in math_content

        if has_equation:
            code = f"""from manim import *

class MathematicalScene(Scene):
    def construct(self):
        # Create equation
        equation = MathTex(r"E = mc^2")

        # Position and style
        equation.scale(2)
        equation.set_color("{primary_color.upper()}")

        # Animation sequence
        self.play(Write(equation), run_time={duration * 0.6})

        # Add some transformation if requested
        if "transform" in "{prompt}".lower():
            new_equation = MathTex(r"F = ma")
            new_equation.scale(2)
            new_equation.set_color(GREEN)
            self.play(Transform(equation, new_equation), run_time={duration * 0.4})

        self.wait(1)
"""
        else:
            code = f"""from manim import *

class AnimatedScene(Scene):
    def construct(self):
        # Create animated text
        text = Text("{prompt[:20]}...")
        text.scale(1.5)
        text.set_color("{primary_color.upper()}")

        # Animation
        self.play(Write(text), run_time={duration * 0.8})
        self.play(text.animate.scale(1.2), run_time={duration * 0.2})
        self.wait(0.5)
"""

        return {
            {
                "engine": "manim",
                "code": code,
                "config": {
                    {
                        "scene_name": "MathematicalScene",
                        "quality": "high_quality",
                        "format": "mp4",
                    }
                },
                "output_filename": "manim_scene.mp4",
            }
        }

    def _get_text_template(
        self, prompt: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate text-based animation code (defaults to Remotion)."""
        return self._get_remotion_template(prompt, parameters)


class AIService:
    """Main AI service for natural language video generation."""

    def __init__(self):
        self.prompt_parser = PromptParser()
        self.code_generator = CodeGenerator()

    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process a natural language prompt and generate video specifications."""
        try:
            # Parse the prompt
            scene_type = self.prompt_parser.extract_scene_type(prompt)
            parameters = self.prompt_parser.extract_parameters(prompt)

            # Generate code for the appropriate engine
            code_spec = self.code_generator.generate_code(
                scene_type, prompt, parameters
            )

            # Create complete specification
            spec = {
                {
                    "original_prompt": prompt,
                    "scene_type": scene_type,
                    "parameters": parameters,
                    "code_spec": code_spec,
                    "pipeline": self._create_pipeline_spec(code_spec),
                    "timestamp": datetime.now().isoformat(),
                }
            }

            logger.info(f"Processed prompt: {prompt[:50]}... -> {scene_type}")
            return spec

        except Exception as e:
            logger.error(f"Failed to process prompt '{prompt}': {str(e)}")
            raise

    def _create_pipeline_spec(self, code_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create the pipeline specification for rendering."""
        pipeline = []

        # Add the main rendering step
        pipeline.append(
            {
                {
                    "type": "render",
                    "engine": code_spec["engine"],
                    "code": code_spec["code"],
                    "config": code_spec["config"],
                    "output": code_spec["output_filename"],
                }
            }
        )

        # Add post-processing with FFmpeg if needed
        if code_spec["engine"] != "ffmpeg":
            pipeline.append(
                {
                    {
                        "type": "post_process",
                        "engine": "ffmpeg",
                        "input": code_spec["output_filename"],
                        "output": "final.mp4",
                        "operations": ["optimize", "compress"],
                    }
                }
            )

        return pipeline

    async def enhance_prompt(self, prompt: str) -> str:
        """Enhance a basic prompt with more descriptive elements."""
        # Simple enhancement - in real implementation, this would use LLM
        enhancements = {
            "short": "Create a smooth, professional animation showing",
            "text": "Create an elegant text animation displaying",
            "math": "Create a mathematical visualization showing",
            "animate": "Create a dynamic animation of",
        }

        words = prompt.split()
        if len(words) < 5:
            for key, enhancement in enhancements.items():
                if key in prompt.lower():
                    return f"{enhancement} {prompt}"
                    break

            # Default enhancement
            return f"Create a professional video showing {prompt}"

        return prompt


# Global AI service instance
ai_service = AIService()
