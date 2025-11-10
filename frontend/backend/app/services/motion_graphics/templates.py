"""
Template generation module for the OMNIVID Motion Graphics Engine.
"""

from typing import Dict, Any, List, Optional
import json
from math import pi
from .core import EffectType, SpeedProfile, AnimationParameters, AnimationEngine


class TemplateGenerator:
    """Generates engine-specific templates from parameters"""
    
    def generate_remotion_template(self, params: AnimationParameters) -> Dict[str, Any]:
        """Generate Remotion composition template"""
        return {
            "composition": {
                "id": f"motion_{params.effect_type.value}",
                "component": "MotionComposition",
                "width": 3840,  # 4K
                "height": 2160,
                "fps": 60 if params.speed == SpeedProfile.ENERGETIC else 30,
                "durationInFrames": int(params.duration * 60),
            },
            "props": {
                "effectType": params.effect_type.value,
                "colors": params.color_scheme,
                "intensity": params.intensity,
                "easing": params.easing,
                "cameraMovement": params.camera_movement,
                "glowEffect": params.glow_effect,
                "rotationSpeed": params.rotation_speed,
                "scale": params.scale_factor,
            },
            "layers": self._generate_layers(params),
        }
    
    def generate_threejs_config(self, params: AnimationParameters) -> Dict[str, Any]:
        """Generate Three.js scene configuration"""
        return {
            "scene": {
                "background": params.color_scheme[0] if params.color_scheme else "#000000",
                "fog": {"enabled": params.blur_amount > 0, "density": params.blur_amount},
            },
            "camera": {
                "type": "PerspectiveCamera",
                "fov": 75,
                "near": 0.1,
                "far": 1000,
                "position": [0, 0, 5],
                "movement": params.camera_movement,
            },
            "particles": {
                "count": params.particle_density * 10,
                "size": 0.1 * params.intensity,
                "velocity": self._speed_to_velocity(params.speed),
                "colors": params.color_scheme,
            },
            "lighting": {
                "ambient": {"color": "#FFFFFF", "intensity": 0.5},
                "point": [
                    {"color": params.color_scheme[0] if params.color_scheme else "#FFFFFF", 
                     "intensity": params.intensity, 
                     "position": [10, 10, 10]},
                    {"color": params.color_scheme[1] if len(params.color_scheme) > 1 else "#FFFFFF", 
                     "intensity": params.intensity * 0.7, 
                     "position": [-10, -10, 10]},
                ],
                "bloom": params.glow_effect,
            },
            "postProcessing": {
                "bloom": {"enabled": params.glow_effect, "strength": 1.5 * params.intensity},
                "dof": {"enabled": params.depth_3d, "focusDistance": 5.0, "aperture": 0.025},
                "motion_blur": {"enabled": params.speed in [SpeedProfile.FAST, SpeedProfile.ENERGETIC]},
            },
        }
    
    def generate_manim_script(self, params: AnimationParameters) -> str:
        """Generate Manim Python script"""
        colors = ', '.join(f'"{c}"' for c in params.color_scheme)
        
        return f"""from manim import *

class Motion{params.effect_type.value.title().replace('_', '')}(Scene):
    def construct(self):
        # Colors
        colors = [{colors}]
        
        # Create shapes
        shapes = VGroup(*[
            Circle(radius=0.5 + i*0.2, color=colors[i % len(colors)])
            for i in range({int(params.intensity * 10)})
        ])
        
        # Animation
        self.play(
            *[
                Create(shape, run_time={params.duration / 2})
                for shape in shapes
            ],
            lag_ratio=0.1
        )
        
        # Transform with easing
        self.play(
            *[
                shape.animate(rate_func=rate_functions.{params.easing.replace('ease', '').lower()})
                .scale({params.scale_factor})
                .rotate({params.rotation_speed * pi / 180})
                for shape in shapes
            ],
            run_time={params.duration / 2}
        )
        
        self.wait(0.5)
"""
    
    def generate_gsap_timeline(self, params: AnimationParameters) -> Dict[str, Any]:
        """Generate GSAP timeline configuration"""
        return {
            "timeline": {
                "duration": params.duration,
                "ease": params.easing,
                "repeat": 0,
            },
            "animations": [
                {
                    "target": ".motion-element",
                    "from": {"opacity": 0, "scale": 0, "rotation": 0},
                    "to": {
                        "opacity": 1,
                        "scale": params.scale_factor,
                        "rotation": params.rotation_speed,
                    },
                    "duration": params.duration * 0.6,
                    "ease": params.easing,
                    "stagger": 0.1,
                },
                {
                    "target": ".particle",
                    "from": {"y": 0, "opacity": 1},
                    "to": {"y": -200, "opacity": 0},
                    "duration": params.duration * 0.4,
                    "ease": "power2.out",
                    "repeat": -1,
                },
            ],
        }
    
    def generate_ffmpeg_pipeline(self, params: AnimationParameters, 
                               input_path: str) -> List[str]:
        """Generate FFmpeg post-processing pipeline"""
        filters = []
        
        # Glow effect
        if params.glow_effect:
            filters.append("gblur=sigma=5")
            filters.append("eq=brightness=0.1:saturation=1.5")
        
        # Blur
        if params.blur_amount > 0:
            filters.append(f"boxblur={int(params.blur_amount)}")
        
        # Color grading
        filters.append("eq=contrast=1.2:brightness=0.05:saturation=1.3")
        
        # Motion blur for fast animations
        if params.speed in [SpeedProfile.FAST, SpeedProfile.ENERGETIC]:
            filters.append("minterpolate=fps=120:mi_mode=mci")
        
        # Chromatic aberration for glitch
        if params.effect_type == EffectType.GLITCH:
            filters.append(
                "split[a][b],[a]lutrgb=r=0:g=0[a1],[b]lutrgb=r=0:b=0[b1],[a1][b1]blend=all_mode=addition"
            )
        
        return filters
    
    def _generate_layers(self, params: AnimationParameters) -> List[Dict[str, Any]]:
        """Generate composition layers"""
        layers = []
        
        # Background layer
        layers.append({
            "type": "solid",
            "color": params.color_scheme[0] if params.color_scheme else "#000000",
            "opacity": 1.0,
        })
        
        # Main effect layer
        layers.append({
            "type": params.effect_type.value,
            "duration": params.duration,
            "intensity": params.intensity,
            "colors": params.color_scheme,
        })
        
        # Particle layer if needed
        if params.particle_density > 0:
            layers.append({
                "type": "particles",
                "count": params.particle_density,
                "colors": params.color_scheme,
                "physics": params.physics_enabled,
            })
        
        # Glow overlay
        if params.glow_effect:
            layers.append({
                "type": "glow_overlay",
                "color": params.color_scheme[1] if len(params.color_scheme) > 1 else "#FFFFFF",
                "intensity": params.intensity * 0.5,
                "blendMode": "screen",
            })
        
        return layers
    
    def _speed_to_velocity(self, speed: SpeedProfile) -> float:
        """Convert speed profile to numeric velocity"""
        velocity_map = {
            SpeedProfile.SLOW: 0.5,
            SpeedProfile.MEDIUM: 1.0,
            SpeedProfile.FAST: 2.0,
            SpeedProfile.ENERGETIC: 3.0,
            SpeedProfile.SMOOTH: 0.8,
            SpeedProfile.SNAPPY: 2.5,
        }
        return velocity_map.get(speed, 1.0)
