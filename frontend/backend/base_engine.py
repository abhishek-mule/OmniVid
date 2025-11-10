"""
BaseEngine Adapter

Abstract class that unifies APIs for different rendering engines
(Remotion, FFmpeg, Blender, Manim, and other motion graphics/animation libraries).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path


class EngineType(Enum):
    """Supported rendering engine types."""
    REMOTION = "remotion"
    FFMPEG = "ffmpeg"
    BLENDER = "blender"
    MANIM = "manim"
    CUSTOM = "custom"


class RenderStatus(Enum):
    """Status of rendering operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RenderConfig:
    """Configuration for rendering operations."""
    output_path: str
    width: int = 1920
    height: int = 1080
    fps: int = 30
    duration: Optional[float] = None
    quality: str = "high"  # low, medium, high, ultra
    codec: Optional[str] = None
    format: str = "mp4"
    additional_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


@dataclass
class RenderResult:
    """Result of a rendering operation."""
    status: RenderStatus
    output_path: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseEngine(ABC):
    """
    Abstract base class for rendering engine adapters.
    
    All engine implementations must inherit from this class and implement
    the required abstract methods to ensure a consistent API across different engines.
    """
    
    def __init__(self, engine_type: EngineType, **kwargs):
        """
        Initialize the engine adapter.
        
        Args:
            engine_type: Type of rendering engine
            **kwargs: Additional engine-specific configuration
        """
        self.engine_type = engine_type
        self.config = kwargs
        self._initialized = False
        self._current_project = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the rendering engine.
        
        Perform any necessary setup, dependency checks, or initialization
        required before the engine can be used.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate that the engine environment is correctly configured.
        
        Check for required dependencies, executables, libraries, etc.
        
        Returns:
            Dict containing validation results with keys:
                - valid (bool): Whether environment is valid
                - issues (List[str]): List of any issues found
                - version (str): Engine version if available
        """
        pass
    
    @abstractmethod
    def create_project(self, project_name: str, **kwargs) -> Any:
        """
        Create a new project or scene in the engine.
        
        Args:
            project_name: Name of the project
            **kwargs: Additional project-specific parameters
            
        Returns:
            Project object or identifier
        """
        pass
    
    @abstractmethod
    def add_asset(self, asset_path: str, asset_type: str, **kwargs) -> str:
        """
        Add an asset (image, video, audio, etc.) to the project.
        
        Args:
            asset_path: Path to the asset file
            asset_type: Type of asset (image, video, audio, text, etc.)
            **kwargs: Additional asset-specific parameters
            
        Returns:
            str: Asset identifier or reference
        """
        pass
    
    @abstractmethod
    def add_scene(self, scene_config: Dict[str, Any]) -> str:
        """
        Add a scene or composition to the project.
        
        Args:
            scene_config: Configuration dictionary for the scene including:
                - name: Scene name
                - duration: Scene duration
                - layers: List of layers/elements
                - transitions: Transition effects
                - animations: Animation configurations
                
        Returns:
            str: Scene identifier
        """
        pass
    
    @abstractmethod
    def apply_effect(self, target_id: str, effect_type: str, **params) -> bool:
        """
        Apply an effect or transformation to a target element.
        
        Args:
            target_id: Identifier of the target element
            effect_type: Type of effect (blur, fade, scale, rotate, etc.)
            **params: Effect-specific parameters
            
        Returns:
            bool: True if effect was applied successfully
        """
        pass
    
    @abstractmethod
    def animate(self, target_id: str, animation_config: Dict[str, Any]) -> bool:
        """
        Add animation to a target element.
        
        Args:
            target_id: Identifier of the target element
            animation_config: Animation configuration including:
                - property: Property to animate (position, scale, opacity, etc.)
                - start_value: Starting value
                - end_value: Ending value
                - duration: Animation duration
                - easing: Easing function
                - delay: Start delay
                
        Returns:
            bool: True if animation was added successfully
        """
        pass
    
    @abstractmethod
    def render(self, config: RenderConfig) -> RenderResult:
        """
        Render the project to output file.
        
        Args:
            config: Rendering configuration
            
        Returns:
            RenderResult: Result of the rendering operation
        """
        pass
    
    @abstractmethod
    def render_async(self, config: RenderConfig, callback: Optional[callable] = None) -> str:
        """
        Start asynchronous rendering operation.
        
        Args:
            config: Rendering configuration
            callback: Optional callback function for progress updates
            
        Returns:
            str: Render job identifier
        """
        pass
    
    @abstractmethod
    def get_render_status(self, job_id: str) -> RenderStatus:
        """
        Get the status of an asynchronous render job.
        
        Args:
            job_id: Render job identifier
            
        Returns:
            RenderStatus: Current status of the render job
        """
        pass
    
    @abstractmethod
    def cancel_render(self, job_id: str) -> bool:
        """
        Cancel an ongoing render job.
        
        Args:
            job_id: Render job identifier
            
        Returns:
            bool: True if cancellation was successful
        """
        pass
    
    @abstractmethod
    def export_project(self, export_path: str, format: str = "json") -> bool:
        """
        Export project configuration to a file.
        
        Args:
            export_path: Path where project should be exported
            format: Export format (json, xml, native, etc.)
            
        Returns:
            bool: True if export was successful
        """
        pass
    
    @abstractmethod
    def import_project(self, import_path: str) -> Any:
        """
        Import a project from a file.
        
        Args:
            import_path: Path to the project file
            
        Returns:
            Project object or identifier
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Clean up resources and temporary files.
        
        Returns:
            bool: True if cleanup was successful
        """
        pass
    
    # Common utility methods (implemented in base class)
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized
    
    def get_engine_type(self) -> EngineType:
        """Get the engine type."""
        return self.engine_type
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported output formats.
        Default implementation, can be overridden.
        """
        return ["mp4", "mov", "avi", "webm", "gif"]
    
    def get_supported_codecs(self) -> List[str]:
        """
        Get list of supported codecs.
        Default implementation, can be overridden.
        """
        return ["h264", "h265", "vp9", "prores"]
    
    def validate_config(self, config: RenderConfig) -> bool:
        """
        Validate rendering configuration.
        Default implementation with common checks.
        """
        if config.width <= 0 or config.height <= 0:
            return False
        if config.fps <= 0:
            return False
        if config.format not in self.get_supported_formats():
            return False
        return True
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False
