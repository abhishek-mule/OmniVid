"""
Main engine module for the OMNIVID Motion Graphics Engine.
"""

import asyncio
from typing import Dict, Any, List, Optional
from .parser import PromptParser
from .router import EngineRouter
from .templates import TemplateGenerator
from .core import EffectType, SpeedProfile, AnimationParameters, EngineMapping


class MotionGraphicsEngine:
    """Main orchestration engine"""
    
    def __init__(self):
        self.parser = PromptParser()
        self.router = EngineRouter()
        self.template_gen = TemplateGenerator()
    
    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Process natural language prompt into complete pipeline"""
        print(f"\n{'='*60}")
        print(f"Processing: {prompt}")
        print(f"{'='*60}\n")
        
        # Parse prompt
        params = self.parser.parse(prompt)
        print(f"✓ Parsed Parameters:")
        print(f"  Effect: {params.effect_type.value}")
        print(f"  Speed: {params.speed.value}")
        print(f"  Duration: {params.duration}s")
        print(f"  Intensity: {params.intensity}")
        print(f"  Colors: {params.color_scheme}")
        print(f"  Particles: {params.particle_density}/s")
        print(f"  Easing: {params.easing}")
        print(f"  3D Depth: {params.depth_3d}")
        print(f"  Glow: {params.glow_effect}")
        print(f"  Camera Movement: {params.camera_movement}\n")
        
        # Route to engines
        mapping = self.router.route(params)
        print(f"✓ Engine Routing:")
        print(f"  Primary: {mapping.primary_engine.value}")
        print(f"  Secondary: {[e.value for e in mapping.secondary_engines]}")
        print(f"  Post-Processing: {mapping.post_processing}\n")
        
        # Generate templates
        templates = {
            "remotion": self.template_gen.generate_remotion_template(params),
            "threejs": self.template_gen.generate_threejs_config(params),
            "manim": self.template_gen.generate_manim_script(params),
            "gsap": self.template_gen.generate_gsap_timeline(params),
            "ffmpeg_filters": self.template_gen.generate_ffmpeg_pipeline(params, "input.mp4"),
        }
        
        print(f"✓ Generated Templates:")
        print(f"  Remotion Composition: 4K @ {templates['remotion']['composition']['fps']}fps")
        print(f"  Three.js Particles: {templates['threejs']['particles']['count']}")
        print(f"  GSAP Timeline: {len(templates['gsap']['animations'])} animations")
        print(f"  FFmpeg Filters: {len(templates['ffmpeg_filters'])} filters\n")
        
        # Build complete pipeline
        pipeline = {
            "parameters": {
                "effect_type": params.effect_type.value,
                "speed": params.speed.value,
                "duration": params.duration,
                "intensity": params.intensity,
                "colors": params.color_scheme,
                "particle_density": params.particle_density,
                "easing": params.easing,
                "camera_movement": params.camera_movement,
                "depth_3d": params.depth_3d,
                "glow_effect": params.glow_effect,
                "blur_amount": params.blur_amount,
                "rotation_speed": params.rotation_speed,
                "scale_factor": params.scale_factor,
                "physics_enabled": params.physics_enabled,
                "sound_reactive": params.sound_reactive,
            },
            "routing": {
                "primary_engine": mapping.primary_engine.value,
                "secondary_engines": [e.value for e in mapping.secondary_engines],
                "post_processing": mapping.post_processing,
                "render_priority": mapping.render_priority,
            },
            "templates": templates,
            "execution_plan": self._create_execution_plan(params, mapping, templates),
        }
        
        return pipeline
    
    def _create_execution_plan(
        self, 
        params: AnimationParameters, 
        mapping: EngineMapping, 
        templates: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create step-by-step execution plan"""
        plan = []
        
        # Step 1: Primary engine render
        engine_key = mapping.primary_engine.value.split('js')[0]  # Handle 'threejs' -> 'three'
        plan.append({
            "step": 1,
            "engine": mapping.primary_engine.value,
            "action": "render_primary",
            "config": templates.get(engine_key, {}),
            "output": f"primary_{params.effect_type.value}.mp4",
            "estimated_time": params.duration * 2,
        })
        
        # Step 2: Secondary engine layers
        for idx, engine in enumerate(mapping.secondary_engines[:2], 2):
            engine_key = engine.value.split('js')[0]
            plan.append({
                "step": idx,
                "engine": engine.value,
                "action": "render_layer",
                "config": templates.get(engine_key, {}),
                "output": f"layer_{idx}_{engine_key}.mp4",
                "estimated_time": params.duration,
            })
        
        # Step 3: Composite layers
        if len(plan) > 1:  # Only if we have multiple layers to composite
            plan.append({
                "step": len(plan) + 1,
                "engine": "ffmpeg",
                "action": "composite_layers",
                "inputs": [step["output"] for step in plan],
                "output": "composited.mp4",
                "estimated_time": params.duration * 0.5,
            })
        
        # Step 4: Post-processing
        post_start_step = len(plan) + 1
        for idx, effect in enumerate(mapping.post_processing, post_start_step):
            plan.append({
                "step": idx,
                "engine": "ffmpeg",
                "action": f"apply_{effect}",
                "filter": effect,
                "input": plan[-1]["output"] if plan else "input.mp4",
                "output": f"processed_{effect}.mp4",
                "estimated_time": params.duration * 0.3,
            })
        
        # Step 5: Final export
        plan.append({
            "step": len(plan) + 1,
            "engine": "ffmpeg",
            "action": "export_4k",
            "input": plan[-1]["output"] if plan else "input.mp4",
            "output": f"final_{params.effect_type.value}_4k.mp4",
            "codec": "libx265",
            "preset": "slow",
            "crf": 18,
            "estimated_time": params.duration * 0.5,
        })
        
        return plan
