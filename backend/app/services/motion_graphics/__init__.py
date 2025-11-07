"""
OMNIVID AI Motion Graphics Backend

This module provides AI-driven motion graphics generation capabilities.
It converts natural language prompts into cinematic videos using various
rendering engines and post-processing effects.
"""

from .core import (
    EffectType,
    AnimationEngine,
    SpeedProfile,
    AnimationParameters,
    MotionGraphicsEngine,
    MotionGraphicsAPI,
    AudioReactiveEngine,
    PhysicsSimulator,
    TemplateLibrary
)

__all__ = [
    'EffectType',
    'AnimationEngine',
    'SpeedProfile',
    'AnimationParameters',
    'MotionGraphicsEngine',
    'MotionGraphicsAPI',
    'AudioReactiveEngine',
    'PhysicsSimulator',
    'TemplateLibrary',
]
