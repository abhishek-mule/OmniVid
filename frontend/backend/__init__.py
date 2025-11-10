"""
OMNIVID Backend

AI-powered video generation and orchestration engine.
"""

__version__ = "0.1.0"
__author__ = "OMNIVID Team"

from .base_engine import BaseEngine, EngineType, RenderConfig, RenderResult, RenderStatus
from .remotion_adapter import RemotionAdapter

__all__ = [
    "BaseEngine",
    "EngineType",
    "RenderConfig",
    "RenderResult",
    "RenderStatus",
    "RemotionAdapter"
]
