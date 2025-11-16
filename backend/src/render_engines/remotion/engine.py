"""
Remotion render engine implementation.
"""
import os
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any
import json
import logging

from .base import RenderEngine, RenderEngineType, RenderResult, RenderStatus

logger = logging.getLogger(__name__)

class RemotionRenderEngine(RenderEngine):
    """Remotion render engine for React-based video creation."""
    
    def __init__(self):
        super().__init__("Remotion", ["mp4", "webm"])
        self.remotion_path = None
        self.temp_dir = None
        self.node_modules = None
    
    def initialize(self) -> bool:
        """Initialize Remotion and check if it's available."""
        try:
            # Check if npx remotion is available
            result = subprocess.run(
                ["npx", "remotion", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.remotion_path = "npx remotion"
                self.version = result.stdout.strip()
                self.is_available = True
                logger.info(f"Remotion initialized successfully: {self.version}")
                return True
            
            logger.warning("Remotion not found or not accessible")
            return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Remotion: {str(e)}")
            return False
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate Remotion-specific settings."""
        try:
            # Basic validation for Remotion settings
            resolution = settings.get("resolution", (1920, 1080))
            if not isinstance(resolution, (tuple, list)) or len(resolution) != 2:
                return False
            
            # Check if React components are specified
            components = settings.get("components", [])
            if not isinstance(components, list):
                return False
            
            return True
            
        except Exception:
            return False
    
    def create_scene(self, prompt: str, settings: Dict[str, Any]) -> str:
        """Create a Remotion project from prompt."""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="omnivid_remotion_")
            
            # Initialize Remotion project
            init_cmd = self.remotion_path.split() + ["new", "--template", "blank"]
            subprocess.run(
                init_cmd,
                cwd=self.temp_dir,
                capture_output=True,
                timeout=60
            )
            
            # Generate React components
            components = self._generate_react_components(prompt, settings)
            
            # Save component files
            src_dir = os.path.join(self.temp_dir, "src")
            os.makedirs(src_dir, exist_ok=True)
            
            # Save main component
            main_component = os.path.join(src_dir, "Video.tsx")
            with open(main_component, 'w') as f:
                f.write(components["main"])
            
            # Save other components
            for name, code in components["other"].items():
                component_file = os.path.join(src_dir, f"{name}.tsx")
                with open(component_file, 'w') as f:
                    f.write(code)
            
            return main_component
            
        except Exception as e:
            logger.error(f"Error creating Remotion scene: {str(e)}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise
    
    def render_video(self, scene_path: str, output_path: str, progress_callback=None) -> RenderResult:
        """Render video using Remotion."""
        try:
            if progress_callback:
                progress_callback(0, RenderStatus.INITIALIZING, "Starting Remotion render")
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if progress_callback:
                progress_callback(20, RenderStatus.RENDERING, "Installing dependencies")
            
            # Install dependencies if needed
            self._ensure_dependencies()
            
            if progress_callback:
                progress_callback(40, RenderStatus.RENDERING, "Compiling React components")
            
            # Build Remotion project
            build_cmd = self.remotion_path.split() + ["render", "Video", output_path, "--concurrency", "1"]
            
            if progress_callback:
                progress_callback(60, RenderStatus.RENDERING, "Rendering video frames")
            
            result = subprocess.run(
                build_cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(90, RenderStatus.POST_PROCESSING, "Finalizing")
                
                # Check if output file exists
                if os.path.exists(output_path):
                    if progress_callback:
                        progress_callback(100, RenderStatus.COMPLETED, "Render completed")
                    
                    return RenderResult(
                        success=True,
                        video_url=output_path,
                        duration=10.0,  # Default duration
                        resolution=(1920, 1080),
                        metadata={
                            "render_engine": "remotion",
                            "remotion_version": self.version,
                            "components": settings.get("components", [])
                        }
                    )
                else:
                    raise RuntimeError("Remotion output file not found")
            else:
                error_msg = f"Remotion render failed: {result.stderr}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(0, RenderStatus.FAILED, error_msg)
                
                return RenderResult(
                    success=False,
                    error_message=error_msg,
                    metadata={"stderr": result.stderr, "stdout": result.stdout}
                )
                
        except Exception as e:
            error_msg = f"Remotion render error: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(0, RenderStatus.FAILED, error_msg)
            return RenderResult(success=False, error_message=error_msg)
            
        finally:
            self.cleanup()
    
    def cleanup(self) -> bool:
        """Clean up temporary files."""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup Remotion temp files: {str(e)}")
            return False
    
    def _generate_react_components(self, prompt: str, settings: Dict[str, Any]) -> Dict[str, str]:
        """Generate React components from prompt."""
        # Parse prompt for components
        text_content = settings.get("text", prompt)
        animation_type = settings.get("animation", "fade")
        
        # Main component
        main_component = f'''
import {{ {{ Composition }} }} from '@remotion/cli/components';
import {{ interpolate, useCurrentFrame, useVideoConfig }} from 'remotion';

const Video: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps, durationInFrames }} = useVideoConfig();

  const opacity = interpolate(
    frame,
    [0, 30, durationInFrames - 30, durationInFrames],
    [0, 1, 1, 0]
  );

  return (
    <div style={{
      flex: 1,
      backgroundColor: 'black',
      justifyContent: 'center',
      alignItems: 'center',
      display: 'flex',
      fontSize: 60,
      color: 'white',
      opacity,
      fontFamily: 'Arial, sans-serif'
    }}>
      {text_content}
    </div>
  );
}};

const RemotionVideo: React.FC = () => {{
  return (
    <Composition
      id="Video"
      component={{Video}}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
    />
  );
}};

export default RemotionVideo;
'''
        
        # Generate additional components based on prompt
        other_components = {}
        
        if "logo" in prompt.lower():
            other_components["Logo"] = f'''
const Logo: React.FC = () => {{
  return (
    <img 
      src="/logo.png" 
      style={{
        width: 200,
        height: 200,
        marginBottom: 40
      }}
    />
  );
}};
export default Logo;
'''
        
        if "chart" in prompt.lower() or "graph" in prompt.lower():
            other_components["Chart"] = f'''
const Chart: React.FC = () => {{
  return (
    <div style={{ display: 'flex', gap: 20 }}>
      <div style={{ width: 60, height: 200, backgroundColor: '#3b82f6' }} />
      <div style={{ width: 60, height: 150, backgroundColor: '#10b981' }} />
      <div style={{ width: 60, height: 180, backgroundColor: '#f59e0b' }} />
    </div>
  );
}};
export default Chart;
'''
        
        return {
            "main": main_component,
            "other": other_components
        }
    
    def _ensure_dependencies(self):
        """Ensure Remotion dependencies are installed."""
        package_json = os.path.join(self.temp_dir, "package.json")
        if os.path.exists(package_json):
            # Install dependencies
            subprocess.run(
                ["npm", "install"],
                cwd=self.temp_dir,
                capture_output=True,
                timeout=120
            )
    
    def get_supported_resolutions(self) -> List[tuple]:
        """Get Remotion-supported resolutions."""
        return [(1920, 1080), (1280, 720), (854, 480)]
    
    def get_supported_fps(self) -> List[int]:
        """Get Remotion-supported frame rates."""
        return [24, 30, 60]