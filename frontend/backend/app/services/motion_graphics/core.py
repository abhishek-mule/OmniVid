"""
Core components of the OMNIVID Motion Graphics Engine.
"""

import re
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import asyncio


class EffectType(Enum):
    """Motion graphics effect types"""
    LOGO_REVEAL = "logo_reveal"
    PARTICLE_BURST = "particle_burst"
    TEXT_ANIMATION = "text_animation"
    SHAPE_MORPH = "shape_morph"
    KINETIC_TYPE = "kinetic_type"
    GLITCH = "glitch"
    LIQUID_MORPH = "liquid_morph"
    GEOMETRIC_TRANSITION = "geometric_transition"
    LIGHT_RAYS = "light_rays"
    CAMERA_ZOOM = "camera_zoom"
    ROTATION_3D = "rotation_3d"
    PARALLAX = "parallax"


class AnimationEngine(Enum):
    """Available animation engines"""
    REMOTION = "remotion"  # React-based video
    FRAMER = "framer"  # UI animations
    MANIM = "manim"  # Mathematical animations
    THREEJS = "threejs"  # 3D graphics
    GSAP = "gsap"  # Timeline animations
    ANIMEJS = "animejs"  # Lightweight animations
    MOJS = "mojs"  # Motion graphics
    FFMPEG = "ffmpeg"  # Post-processing


class SpeedProfile(Enum):
    """Animation speed profiles"""
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"
    ENERGETIC = "energetic"
    SMOOTH = "smooth"
    SNAPPY = "snappy"


@dataclass
class AnimationParameters:
    """Extracted animation parameters from prompt"""
    effect_type: EffectType
    speed: SpeedProfile
    duration: float  # seconds
    intensity: float  # 0-1
    color_scheme: List[str]
    particle_density: int  # particles per second
    easing: str  # easing function
    camera_movement: bool
    depth_3d: bool
    glow_effect: bool
    blur_amount: float
    rotation_speed: float
    scale_factor: float
    physics_enabled: bool
    sound_reactive: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineMapping:
    """Maps effect types to animation engines"""
    primary_engine: AnimationEngine
    secondary_engines: List[AnimationEngine]
    post_processing: List[str]
    render_priority: int
