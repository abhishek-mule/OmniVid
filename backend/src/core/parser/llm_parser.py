"""
LLM Parser for natural language to scene JSON conversion.
"""
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SceneJSON:
    """Structured scene representation."""

    def __init__(self):
        self.version = "1.0"
        self.metadata = {}
        self.timeline = []
        self.assets = []
        self.settings = {}

    def add_scene(self, scene_data: Dict[str, Any]):
        """Add a scene to the timeline."""
        self.timeline.append(scene_data)

    def add_asset(self, asset_data: Dict[str, Any]):
        """Add an asset reference."""
        self.assets.append(asset_data)

    def set_global_settings(self, settings: Dict[str, Any]):
        """Set global video settings."""
        self.settings.update(settings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "metadata": self.metadata,
            "timeline": self.timeline,
            "assets": self.assets,
            "settings": self.settings
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

class LLMParser:
    """Converts natural language prompts to structured Scene JSON."""

    def __init__(self):
        self.scene_types = {
            'text': ['text', 'title', 'headline', 'typography'],
            'animation': ['animate', 'motion', 'movement', 'transition'],
            'math': ['equation', 'formula', 'graph', 'function', 'mathematical'],
            'web': ['ui', 'interface', 'component', 'react', 'web'],
            '3d': ['3d', 'cube', 'sphere', 'cylinder', 'object']
        }

    def parse(self, prompt: str) -> SceneJSON:
        """Parse natural language prompt into SceneJSON."""
        scene_json = SceneJSON()

        # Extract basic metadata
        scene_json.metadata = {
            "original_prompt": prompt,
            "parsed_at": datetime.now().isoformat(),
            "scene_count": 1,  # Start with 1 scene
            "estimated_duration": self._estimate_duration(prompt)
        }

        # Determine primary scene type
        scene_type = self._detect_scene_type(prompt)

        # Extract settings
        global_settings = self._extract_global_settings(prompt)
        scene_json.set_global_settings(global_settings)

        # Create scene data
        scene_data = self._create_scene_data(prompt, scene_type, global_settings)
        scene_json.add_scene(scene_data)

        return scene_json

    def _detect_scene_type(self, prompt: str) -> str:
        """Detect the primary scene type from the prompt."""
        prompt_lower = prompt.lower()

        for scene_type, keywords in self.scene_types.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return scene_type

        # Default to animation if nothing specific detected
        return 'animation'

    def _extract_global_settings(self, prompt: str) -> Dict[str, Any]:
        """Extract global video settings from prompt."""
        settings = {
            "resolution": self._parse_resolution(prompt),
            "duration": self._parse_duration(prompt),
            "fps": self._parse_fps(prompt),
            "colors": self._parse_colors(prompt),
            "style": self._parse_style(prompt)
        }

        return settings

    def _create_scene_data(self, prompt: str, scene_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create scene data dictionary."""
        return {
            "id": f"scene_{scene_type}_1",
            "type": scene_type,
            "start_time": 0.0,
            "duration": settings.get("duration", 5.0),
            "engine": self._select_engine(scene_type),
            "content": self._extract_content(prompt, scene_type),
            "animations": self._extract_animations(prompt),
            "style": settings.get("style", "modern")
        }

    def _select_engine(self, scene_type: str) -> str:
        """Select appropriate rendering engine for scene type."""
        engine_map = {
            'text': 'remotion',
            'animation': 'remotion',
            'math': 'manim',
            'web': 'remotion',
            '3d': 'blender'
        }
        return engine_map.get(scene_type, 'remotion')

    def _extract_content(self, prompt: str, scene_type: str) -> Dict[str, Any]:
        """Extract content-specific data from prompt."""
        if scene_type == 'text':
            return {"text": self._extract_text_content(prompt)}
        elif scene_type == 'math':
            return {"equation": self._extract_math_content(prompt)}
        elif scene_type == 'animation':
            return {"description": prompt}
        else:
            return {"description": prompt}

    def _extract_text_content(self, prompt: str) -> str:
        """Extract text content from prompt."""
        # Remove action verbs and styling words
        text = re.sub(r'\b(create|make|show|display|animate)\b', '', prompt, flags=re.IGNORECASE)
        text = re.sub(r'\b(with|using|in|on|a|an|the)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip()

        # Try to find quoted text first
        quotes = re.findall(r'"([^"]+)"', prompt)
        if quotes:
            return quotes[0]

        # Return cleaned text or default
        return text or "Generated Text"

    def _extract_math_content(self, prompt: str) -> str:
        """Extract mathematical content."""
        # Look for LaTeX-style equations
        latex_patterns = [
            r'\$\$([^$]+)\$\$',  # $$equation$$
            r'\$([^$]+)\$',      # $equation$
            r'E\s*=\s*mc\^2',    # E = mc^2
            r'F\s*=\s*ma',       # F = ma
        ]

        for pattern in latex_patterns:
            match = re.search(pattern, prompt)
            if match:
                return match.group(1).strip()

        # Default mathematical content
        return r"E = mc^2"

    def _extract_animations(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract animation specifications."""
        animations = []

        if 'fade' in prompt.lower():
            animations.append({
                "type": "fade",
                "direction": "in" if 'fade in' in prompt.lower() else "out",
                "duration": 1.0
            })

        if 'slide' in prompt.lower():
            animations.append({
                "type": "slide",
                "direction": "left" if 'left' in prompt.lower() else "right",
                "duration": 0.8
            })

        if 'scale' in prompt.lower() or 'grow' in prompt.lower():
            animations.append({
                "type": "scale",
                "start_scale": 0.8,
                "end_scale": 1.2,
                "duration": 0.5
            })

        # Default animation if none specified
        if not animations:
            animations.append({
                "type": "fade",
                "direction": "in",
                "duration": 0.5
            })

        return animations

    def _parse_resolution(self, prompt: str) -> str:
        """Parse resolution from prompt."""
        if '4k' in prompt.lower() or 'ultra' in prompt.lower():
            return "3840x2160"
        elif '1080p' in prompt.lower() or 'full hd' in prompt.lower():
            return "1920x1080"
        elif '720p' in prompt.lower() or 'hd' in prompt.lower():
            return "1280x720"
        return "1920x1080"

    def _parse_duration(self, prompt: str) -> float:
        """Parse duration from prompt."""
        duration_match = re.search(r'(\d+)\s*(second|minute)s?', prompt.lower())
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            return value * 60 if unit == 'minute' else value
        return 5.0

    def _parse_fps(self, prompt: str) -> int:
        """Parse FPS from prompt."""
        if '60' in prompt:
            return 60
        elif '30' in prompt:
            return 30
        elif '24' in prompt:
            return 24
        return 30

    def _parse_colors(self, prompt: str) -> List[str]:
        """Parse color preferences."""
        colors = []
        color_keywords = {
            'blue': ['blue', 'navy', 'azure'],
            'green': ['green', 'emerald', 'teal'],
            'red': ['red', 'crimson', 'scarlet'],
            'purple': ['purple', 'violet', 'lavender'],
            'orange': ['orange', 'amber'],
            'yellow': ['yellow', 'gold'],
            'black': ['black', 'dark'],
            'white': ['white', 'light']
        }

        prompt_lower = prompt.lower()
        for color, keywords in color_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                colors.append(color)
                break  # Take first color found

        return colors or ['blue']

    def _parse_style(self, prompt: str) -> str:
        """Parse visual style."""
        if 'minimal' in prompt.lower() or 'clean' in prompt.lower():
            return 'minimal'
        elif 'corporate' in prompt.lower() or 'professional' in prompt.lower():
            return 'corporate'
        elif 'vibrant' in prompt.lower() or 'colorful' in prompt.lower():
            return 'vibrant'
        return 'modern'

    def _estimate_duration(self, prompt: str) -> float:
        """Estimate total duration based on prompt complexity."""
        words = len(prompt.split())
        base_duration = 5.0

        # Longer prompts might need more time
        if words > 20:
            base_duration += 2.0
        if words > 50:
            base_duration += 3.0

        return base_duration

# Global parser instance
parser = LLMParser()
