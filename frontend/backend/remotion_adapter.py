"""
RemotionAdapter

Concrete implementation of BaseEngine for Remotion rendering engine.
Wraps Remotion's CLI for programmatic video rendering.
"""

import json
import subprocess
import uuid
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from threading import Thread

from base_engine import (
    BaseEngine,
    EngineType,
    RenderConfig,
    RenderResult,
    RenderStatus
)


class RemotionAdapter(BaseEngine):
    """
    Adapter for Remotion rendering engine.
    
    Remotion uses React components to create videos programmatically.
    This adapter wraps the Remotion CLI to enable rendering from Python.
    """
    
    def __init__(self, 
                 remotion_root: str = None,
                 composition_id: str = "MyComposition",
                 node_path: str = "node",
                 npx_path: str = "npx",
                 **kwargs):
        """
        Initialize the Remotion adapter.
        
        Args:
            remotion_root: Path to Remotion project root
            composition_id: Default composition ID to render
            node_path: Path to Node.js executable
            npx_path: Path to npx executable
            **kwargs: Additional configuration
        """
        super().__init__(EngineType.REMOTION, **kwargs)
        self.remotion_root = Path(remotion_root) if remotion_root else Path.cwd()
        self.composition_id = composition_id
        self.node_path = node_path
        self.npx_path = npx_path
        self._render_jobs = {}
        self._assets = {}
        self._scenes = {}
        self._input_props = {}
        
    def initialize(self) -> bool:
        """Initialize the Remotion engine."""
        try:
            # Check if Remotion project exists
            package_json = self.remotion_root / "package.json"
            if not package_json.exists():
                print(f"Warning: package.json not found in {self.remotion_root}")
                return False
            
            # Validate environment
            validation = self.validate_environment()
            if not validation["valid"]:
                print(f"Environment validation failed: {validation['issues']}")
                return False
            
            self._initialized = True
            return True
            
        except Exception as e:
            print(f"Initialization error: {e}")
            return False
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate that Remotion environment is correctly configured."""
        issues = []
        version = None
        
        try:
            # Check Node.js
            node_result = subprocess.run(
                [self.node_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if node_result.returncode != 0:
                issues.append("Node.js not found or not working")
            
            # Check npm/npx
            npx_result = subprocess.run(
                [self.npx_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if npx_result.returncode != 0:
                issues.append("npx not found or not working")
            
            # Check Remotion installation
            try:
                remotion_result = subprocess.run(
                    [self.npx_path, "remotion", "versions"],
                    cwd=str(self.remotion_root),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if remotion_result.returncode == 0:
                    version = remotion_result.stdout.strip()
                else:
                    issues.append("Remotion not installed in project")
            except Exception:
                issues.append("Unable to check Remotion version")
            
            # Check project structure
            if not (self.remotion_root / "package.json").exists():
                issues.append("package.json not found")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "version": version
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "version": None
            }
    
    def create_project(self, project_name: str, **kwargs) -> Any:
        """
        Create a new Remotion project.
        
        Args:
            project_name: Name of the project
            **kwargs: Additional parameters (template, etc.)
            
        Returns:
            Project path
        """
        template = kwargs.get("template", "blank")
        project_path = self.remotion_root / project_name
        
        try:
            # Create Remotion project using CLI
            cmd = [
                self.npx_path,
                "create-video",
                "--template", template,
                str(project_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self._current_project = str(project_path)
                return project_path
            else:
                raise Exception(f"Project creation failed: {result.stderr}")
                
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def add_asset(self, asset_path: str, asset_type: str, **kwargs) -> str:
        """
        Add an asset to the Remotion project.
        
        Assets are typically placed in the public/ directory for Remotion.
        
        Args:
            asset_path: Path to the asset file
            asset_type: Type of asset (image, video, audio, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Asset identifier (relative path in public/)
        """
        asset_id = kwargs.get("asset_id", str(uuid.uuid4()))
        
        try:
            # Copy asset to public directory
            public_dir = self.remotion_root / "public" / "assets"
            public_dir.mkdir(parents=True, exist_ok=True)
            
            asset_file = Path(asset_path)
            dest_path = public_dir / asset_file.name
            
            shutil.copy2(asset_path, dest_path)
            
            # Store asset reference
            relative_path = f"assets/{asset_file.name}"
            self._assets[asset_id] = {
                "path": str(dest_path),
                "relative_path": relative_path,
                "type": asset_type,
                "original_path": asset_path
            }
            
            return asset_id
            
        except Exception as e:
            print(f"Error adding asset: {e}")
            return ""
    
    def add_scene(self, scene_config: Dict[str, Any]) -> str:
        """
        Add a scene configuration.
        
        In Remotion, scenes are typically React components.
        This method stores scene data to be passed as input props.
        
        Args:
            scene_config: Scene configuration
            
        Returns:
            Scene identifier
        """
        scene_id = scene_config.get("id", str(uuid.uuid4()))
        self._scenes[scene_id] = scene_config
        
        # Update input props for Remotion
        self._input_props.setdefault("scenes", []).append(scene_config)
        
        return scene_id
    
    def apply_effect(self, target_id: str, effect_type: str, **params) -> bool:
        """
        Apply an effect to a target element.
        
        Effects in Remotion are typically implemented in React components.
        This stores effect data to be passed as props.
        
        Args:
            target_id: Target element ID
            effect_type: Effect type
            **params: Effect parameters
            
        Returns:
            Success status
        """
        if target_id not in self._scenes and target_id not in self._assets:
            return False
        
        effect_config = {
            "type": effect_type,
            "params": params
        }
        
        # Store effect in input props
        self._input_props.setdefault("effects", {}).setdefault(target_id, []).append(effect_config)
        
        return True
    
    def animate(self, target_id: str, animation_config: Dict[str, Any]) -> bool:
        """
        Add animation to a target element.
        
        Remotion uses React Spring or CSS animations.
        This stores animation data to be passed as props.
        
        Args:
            target_id: Target element ID
            animation_config: Animation configuration
            
        Returns:
            Success status
        """
        if target_id not in self._scenes and target_id not in self._assets:
            return False
        
        # Store animation in input props
        self._input_props.setdefault("animations", {}).setdefault(target_id, []).append(animation_config)
        
        return True
    
    def render(self, config: RenderConfig) -> RenderResult:
        """
        Render the Remotion composition synchronously.
        
        Args:
            config: Rendering configuration
            
        Returns:
            Render result
        """
        if not self.validate_config(config):
            return RenderResult(
                status=RenderStatus.FAILED,
                error="Invalid render configuration"
            )
        
        try:
            # Prepare input props
            input_props = self._prepare_input_props(config)
            
            # Build Remotion render command
            cmd = self._build_render_command(config, input_props)
            
            # Execute render
            result = subprocess.run(
                cmd,
                cwd=str(self.remotion_root),
                capture_output=True,
                text=True,
                timeout=config.additional_params.get("timeout", 600)
            )
            
            if result.returncode == 0:
                return RenderResult(
                    status=RenderStatus.COMPLETED,
                    output_path=config.output_path,
                    metadata={"stdout": result.stdout}
                )
            else:
                return RenderResult(
                    status=RenderStatus.FAILED,
                    error=result.stderr,
                    metadata={"stdout": result.stdout}
                )
                
        except subprocess.TimeoutExpired:
            return RenderResult(
                status=RenderStatus.FAILED,
                error="Render timeout exceeded"
            )
        except Exception as e:
            return RenderResult(
                status=RenderStatus.FAILED,
                error=str(e)
            )
    
    def render_async(self, config: RenderConfig, callback: Optional[callable] = None) -> str:
        """
        Start asynchronous rendering operation.
        
        Args:
            config: Rendering configuration
            callback: Optional callback for progress updates
            
        Returns:
            Render job ID
        """
        job_id = str(uuid.uuid4())
        
        def render_thread():
            self._render_jobs[job_id] = {"status": RenderStatus.IN_PROGRESS}
            result = self.render(config)
            self._render_jobs[job_id] = {
                "status": result.status,
                "result": result
            }
            if callback:
                callback(job_id, result)
        
        thread = Thread(target=render_thread, daemon=True)
        thread.start()
        
        self._render_jobs[job_id] = {"status": RenderStatus.PENDING, "thread": thread}
        
        return job_id
    
    def get_render_status(self, job_id: str) -> RenderStatus:
        """Get the status of a render job."""
        job = self._render_jobs.get(job_id)
        if not job:
            return RenderStatus.FAILED
        return job.get("status", RenderStatus.FAILED)
    
    def cancel_render(self, job_id: str) -> bool:
        """
        Cancel a render job.
        
        Note: Cancellation support is limited with subprocess.
        """
        job = self._render_jobs.get(job_id)
        if not job:
            return False
        
        job["status"] = RenderStatus.CANCELLED
        return True
    
    def export_project(self, export_path: str, format: str = "json") -> bool:
        """
        Export project configuration.
        
        Args:
            export_path: Export file path
            format: Export format (json)
            
        Returns:
            Success status
        """
        try:
            export_data = {
                "engine": "remotion",
                "composition_id": self.composition_id,
                "remotion_root": str(self.remotion_root),
                "assets": self._assets,
                "scenes": self._scenes,
                "input_props": self._input_props
            }
            
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def import_project(self, import_path: str) -> Any:
        """
        Import project configuration.
        
        Args:
            import_path: Import file path
            
        Returns:
            Project data
        """
        try:
            with open(import_path, "r") as f:
                data = json.load(f)
            
            if data.get("engine") != "remotion":
                raise ValueError("Invalid project format")
            
            self.composition_id = data.get("composition_id", self.composition_id)
            self.remotion_root = Path(data.get("remotion_root", self.remotion_root))
            self._assets = data.get("assets", {})
            self._scenes = data.get("scenes", {})
            self._input_props = data.get("input_props", {})
            
            return data
            
        except Exception as e:
            print(f"Import error: {e}")
            return None
    
    def cleanup(self) -> bool:
        """Clean up resources."""
        try:
            self._render_jobs.clear()
            self._assets.clear()
            self._scenes.clear()
            self._input_props.clear()
            self._initialized = False
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get supported output formats for Remotion."""
        return ["mp4", "webm", "mov", "mkv", "gif"]
    
    def get_supported_codecs(self) -> List[str]:
        """Get supported codecs for Remotion."""
        return ["h264", "h265", "vp8", "vp9", "prores"]
    
    def _prepare_input_props(self, config: RenderConfig) -> Dict[str, Any]:
        """Prepare input props for Remotion composition."""
        props = self._input_props.copy()
        
        # Add render config to props
        props["renderConfig"] = {
            "width": config.width,
            "height": config.height,
            "fps": config.fps,
            "duration": config.duration
        }
        
        # Add assets
        props["assets"] = {
            asset_id: asset_data["relative_path"]
            for asset_id, asset_data in self._assets.items()
        }
        
        return props
    
    def _build_render_command(self, config: RenderConfig, input_props: Dict[str, Any]) -> List[str]:
        """Build the Remotion CLI render command."""
        cmd = [
            self.npx_path,
            "remotion", "render",
            self.composition_id,
            config.output_path
        ]
        
        # Add dimensions
        cmd.extend(["--width", str(config.width)])
        cmd.extend(["--height", str(config.height)])
        
        # Add FPS
        cmd.extend(["--fps", str(config.fps)])
        
        # Add codec if specified
        if config.codec:
            cmd.extend(["--codec", config.codec])
        
        # Add quality/CRF
        quality_map = {"low": 28, "medium": 23, "high": 18, "ultra": 15}
        crf = quality_map.get(config.quality, 23)
        cmd.extend(["--crf", str(crf)])
        
        # Add input props as JSON
        if input_props:
            props_json = json.dumps(input_props)
            cmd.extend(["--props", props_json])
        
        # Add additional parameters
        for key, value in config.additional_params.items():
            if key not in ["timeout"]:  # Skip non-CLI params
                cmd.extend([f"--{key}", str(value)])
        
        return cmd
