"""
Prompt parsing module for the OMNIVID Motion Graphics Engine.
"""

import re
from typing import Dict, List, Any, Optional
from .core import EffectType, SpeedProfile, AnimationParameters


class PromptParser:
    """AI-driven natural language prompt parser"""
    
    # Keyword mappings for intelligent extraction
    SPEED_KEYWORDS = {
        "slow": SpeedProfile.SLOW,
        "gentle": SpeedProfile.SLOW,
        "smooth": SpeedProfile.SMOOTH,
        "medium": SpeedProfile.MEDIUM,
        "fast": SpeedProfile.FAST,
        "quick": SpeedProfile.FAST,
        "energetic": SpeedProfile.ENERGETIC,
        "explosive": SpeedProfile.ENERGETIC,
        "snappy": SpeedProfile.SNAPPY,
        "instant": SpeedProfile.SNAPPY,
    }
    
    EFFECT_KEYWORDS = {
        "logo": EffectType.LOGO_REVEAL,
        "particle": EffectType.PARTICLE_BURST,
        "particles": EffectType.PARTICLE_BURST,
        "text": EffectType.TEXT_ANIMATION,
        "type": EffectType.TEXT_ANIMATION,
        "morph": EffectType.SHAPE_MORPH,
        "shape": EffectType.SHAPE_MORPH,
        "kinetic": EffectType.KINETIC_TYPE,
        "glitch": EffectType.GLITCH,
        "liquid": EffectType.LIQUID_MORPH,
        "fluid": EffectType.LIQUID_MORPH,
        "geometric": EffectType.GEOMETRIC_TRANSITION,
        "light": EffectType.LIGHT_RAYS,
        "rays": EffectType.LIGHT_RAYS,
        "zoom": EffectType.CAMERA_ZOOM,
        "spin": EffectType.ROTATION_3D,
        "rotate": EffectType.ROTATION_3D,
        "parallax": EffectType.PARALLAX,
    }
    
    COLOR_PATTERNS = {
        "vibrant": ["#FF00FF", "#00FFFF", "#FF0080"],
        "electric": ["#00F0FF", "#FF00F0", "#F0FF00"],
        "neon": ["#FF006E", "#00FFD1", "#FFBE0B"],
        "cool": ["#4A90E2", "#50E3C2", "#B8E986"],
        "warm": ["#FF6B6B", "#FFD93D", "#FF8C42"],
        "monochrome": ["#FFFFFF", "#CCCCCC", "#666666"],
        "sunset": ["#FF6B35", "#F7931E", "#FDC830"],
        "ocean": ["#0077BE", "#00B4D8", "#90E0EF"],
    }
    
    def parse(self, prompt: str) -> AnimationParameters:
        """Parse natural language prompt into animation parameters"""
        prompt_lower = prompt.lower()
        
        # Extract effect type
        effect_type = self._extract_effect_type(prompt_lower)
        
        # Extract speed profile
        speed = self._extract_speed(prompt_lower)
        
        # Extract duration
        duration = self._extract_duration(prompt_lower)
        
        # Extract intensity
        intensity = self._extract_intensity(prompt_lower)
        
        # Extract color scheme
        colors = self._extract_colors(prompt_lower)
        
        # Extract particle density
        particle_density = self._extract_particle_density(prompt_lower, intensity)
        
        # Extract easing
        easing = self._extract_easing(prompt_lower, speed)
        
        # Detect features
        camera_movement = any(word in prompt_lower for word in ["zoom", "pan", "camera", "dolly"])
        depth_3d = any(word in prompt_lower for word in ["3d", "depth", "perspective", "spatial"])
        glow_effect = any(word in prompt_lower for word in ["glow", "shine", "luminous", "radiant"])
        physics_enabled = any(word in prompt_lower for word in ["gravity", "physics", "bounce", "collision"])
        sound_reactive = any(word in prompt_lower for word in ["sound", "audio", "beat", "reactive"])
        
        # Extract numeric values
        blur_amount = self._extract_numeric(prompt_lower, "blur", 0.0, 10.0, 2.0)
        rotation_speed = self._extract_numeric(prompt_lower, "rotation", 0.0, 360.0, 180.0)
        scale_factor = self._extract_numeric(prompt_lower, "scale", 0.1, 5.0, 1.0)
        
        return AnimationParameters(
            effect_type=effect_type,
            speed=speed,
            duration=duration,
            intensity=intensity,
            color_scheme=colors,
            particle_density=particle_density,
            easing=easing,
            camera_movement=camera_movement,
            depth_3d=depth_3d,
            glow_effect=glow_effect,
            blur_amount=blur_amount,
            rotation_speed=rotation_speed,
            scale_factor=scale_factor,
            physics_enabled=physics_enabled,
            sound_reactive=sound_reactive,
            metadata={"original_prompt": prompt}
        )
    
    def _extract_effect_type(self, prompt: str) -> EffectType:
        """Extract primary effect type from prompt"""
        for keyword, effect in self.EFFECT_KEYWORDS.items():
            if keyword in prompt:
                return effect
        return EffectType.PARTICLE_BURST  # default
    
    def _extract_speed(self, prompt: str) -> SpeedProfile:
        """Extract speed profile from prompt"""
        for keyword, speed in self.SPEED_KEYWORDS.items():
            if keyword in prompt:
                return speed
        return SpeedProfile.MEDIUM  # default
    
    def _extract_duration(self, prompt: str) -> float:
        """Extract duration from prompt"""
        # Look for patterns like "3s", "5 seconds", "2.5s"
        duration_match = re.search(r'(\d+\.?\d*)\s*(s|sec|seconds?)', prompt)
        if duration_match:
            return float(duration_match.group(1))
        
        # Default durations based on speed
        if "quick" in prompt or "fast" in prompt:
            return 2.0
        elif "slow" in prompt:
            return 5.0
        return 3.0
    
    def _extract_intensity(self, prompt: str) -> float:
        """Extract intensity level (0-1)"""
        intensity_words = {
            "subtle": 0.3,
            "gentle": 0.4,
            "medium": 0.5,
            "strong": 0.7,
            "intense": 0.8,
            "extreme": 0.9,
            "explosive": 1.0,
        }
        
        for word, value in intensity_words.items():
            if word in prompt:
                return value
        
        return 0.6  # default
    
    def _extract_colors(self, prompt: str) -> List[str]:
        """Extract color scheme from prompt"""
        for keyword, colors in self.COLOR_PATTERNS.items():
            if keyword in prompt:
                return colors
        
        # Look for hex colors in prompt
        hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', prompt)
        if hex_colors:
            return hex_colors
        
        return ["#FF00FF", "#00FFFF", "#FFFF00"]  # default vibrant
    
    def _extract_particle_density(self, prompt: str, intensity: float) -> int:
        """Calculate particle density based on prompt and intensity"""
        base_density = 100
        
        if "dense" in prompt or "heavy" in prompt:
            return int(base_density * 2 * intensity)
        elif "sparse" in prompt or "light" in prompt:
            return int(base_density * 0.5 * intensity)
        
        return int(base_density * intensity)
    
    def _extract_easing(self, prompt: str, speed: SpeedProfile) -> str:
        """Determine easing function"""
        if "bounce" in prompt:
            return "easeOutBounce"
        elif "elastic" in prompt:
            return "easeOutElastic"
        elif "smooth" in prompt:
            return "easeInOutCubic"
        
        # Speed-based defaults
        easing_map = {
            SpeedProfile.SLOW: "easeInOutQuad",
            SpeedProfile.MEDIUM: "easeInOutCubic",
            SpeedProfile.FAST: "easeOutQuad",
            SpeedProfile.ENERGETIC: "easeOutExpo",
            SpeedProfile.SMOOTH: "easeInOutSine",
            SpeedProfile.SNAPPY: "easeOutBack",
        }
        
        return easing_map.get(speed, "easeInOutCubic")
    
    def _extract_numeric(self, prompt: str, param: str, min_val: float, 
                        max_val: float, default: float) -> float:
        """Extract numeric parameter from prompt"""
        pattern = rf'{param}[\s:]+(\d+\.?\d*)'
        match = re.search(pattern, prompt)
        if match:
            value = float(match.group(1))
            return max(min_val, min(max_val, value))
        return default
