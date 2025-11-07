"""
Engine routing module for the OMNIVID Motion Graphics Engine.
"""

from typing import Dict, List
from .core import EffectType, AnimationEngine, EngineMapping, AnimationParameters


class EngineRouter:
    """Routes animation tasks to appropriate engines"""
    
    ENGINE_MAPPINGS = {
        EffectType.LOGO_REVEAL: EngineMapping(
            primary_engine=AnimationEngine.REMOTION,
            secondary_engines=[AnimationEngine.GSAP, AnimationEngine.THREEJS],
            post_processing=["glow", "color_grade"],
            render_priority=1
        ),
        EffectType.PARTICLE_BURST: EngineMapping(
            primary_engine=AnimationEngine.THREEJS,
            secondary_engines=[AnimationEngine.MOJS, AnimationEngine.REMOTION],
            post_processing=["blur", "glow", "bloom"],
            render_priority=2
        ),
        EffectType.TEXT_ANIMATION: EngineMapping(
            primary_engine=AnimationEngine.FRAMER,
            secondary_engines=[AnimationEngine.GSAP, AnimationEngine.ANIMEJS],
            post_processing=["color_grade"],
            render_priority=1
        ),
        EffectType.SHAPE_MORPH: EngineMapping(
            primary_engine=AnimationEngine.MANIM,
            secondary_engines=[AnimationEngine.ANIMEJS, AnimationEngine.MOJS],
            post_processing=["smooth", "color_grade"],
            render_priority=2
        ),
        EffectType.KINETIC_TYPE: EngineMapping(
            primary_engine=AnimationEngine.GSAP,
            secondary_engines=[AnimationEngine.ANIMEJS, AnimationEngine.REMOTION],
            post_processing=["motion_blur"],
            render_priority=1
        ),
        EffectType.GLITCH: EngineMapping(
            primary_engine=AnimationEngine.REMOTION,
            secondary_engines=[AnimationEngine.FFMPEG],
            post_processing=["rgb_split", "chromatic", "distortion"],
            render_priority=2
        ),
        EffectType.LIQUID_MORPH: EngineMapping(
            primary_engine=AnimationEngine.THREEJS,
            secondary_engines=[AnimationEngine.MOJS],
            post_processing=["blur", "glow"],
            render_priority=3
        ),
        EffectType.GEOMETRIC_TRANSITION: EngineMapping(
            primary_engine=AnimationEngine.MANIM,
            secondary_engines=[AnimationEngine.THREEJS],
            post_processing=["smooth"],
            render_priority=2
        ),
        EffectType.LIGHT_RAYS: EngineMapping(
            primary_engine=AnimationEngine.THREEJS,
            secondary_engines=[AnimationEngine.REMOTION],
            post_processing=["glow", "bloom", "god_rays"],
            render_priority=3
        ),
        EffectType.CAMERA_ZOOM: EngineMapping(
            primary_engine=AnimationEngine.REMOTION,
            secondary_engines=[AnimationEngine.THREEJS],
            post_processing=["depth_of_field", "motion_blur"],
            render_priority=2
        ),
        EffectType.ROTATION_3D: EngineMapping(
            primary_engine=AnimationEngine.THREEJS,
            secondary_engines=[AnimationEngine.REMOTION],
            post_processing=["depth_of_field"],
            render_priority=2
        ),
        EffectType.PARALLAX: EngineMapping(
            primary_engine=AnimationEngine.THREEJS,
            secondary_engines=[AnimationEngine.FRAMER],
            post_processing=["depth_of_field"],
            render_priority=2
        ),
    }
    
    def route(self, params: AnimationParameters) -> EngineMapping:
        """Route animation to appropriate engines"""
        mapping = self.ENGINE_MAPPINGS.get(
            params.effect_type,
            self.ENGINE_MAPPINGS[EffectType.PARTICLE_BURST]
        )
        
        # Create a deep copy of the mapping to avoid modifying the original
        from copy import deepcopy
        mapping = deepcopy(mapping)
        
        # Adjust based on features
        if params.depth_3d and AnimationEngine.THREEJS not in mapping.secondary_engines:
            mapping.secondary_engines.insert(0, AnimationEngine.THREEJS)
        
        if params.physics_enabled and AnimationEngine.MOJS not in mapping.secondary_engines:
            mapping.secondary_engines.insert(0, AnimationEngine.MOJS)
        
        # Add post-processing effects
        if params.glow_effect and "glow" not in mapping.post_processing:
            mapping.post_processing.append("glow")
        
        if params.blur_amount > 0 and "blur" not in mapping.post_processing:
            mapping.post_processing.append("blur")
        
        return mapping
