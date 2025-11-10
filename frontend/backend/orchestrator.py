"""
Orchestrator

Multi-engine orchestration layer for intelligent scene routing and job coordination.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import uuid

from base_engine import BaseEngine, EngineType, RenderConfig, RenderResult, RenderStatus
from remotion_adapter import RemotionAdapter
from ffmpeg_adapter import FFmpegAdapter


class SceneType(Enum):
    """Types of scenes that can be routed to different engines."""
    TEXT_ANIMATION = "text_animation"
    MOTION_GRAPHICS = "motion_graphics"
    VIDEO_COMPOSITION = "video_composition"
    TRANSITION = "transition"
    EFFECT = "effect"
    BACKGROUND = "background"
    OVERLAY = "overlay"


@dataclass
class SceneTask:
    """Represents a single scene rendering task."""
    id: str
    scene_type: SceneType
    engine: EngineType
    config: Dict[str, Any]
    dependencies: List[str]  # IDs of tasks that must complete first
    output_path: Optional[str] = None
    status: RenderStatus = RenderStatus.PENDING
    result: Optional[RenderResult] = None


@dataclass
class OrchestratedJob:
    """Represents a complete orchestrated rendering job."""
    id: str
    name: str
    tasks: List[SceneTask]
    final_output_path: str
    metadata: Dict[str, Any]
    status: RenderStatus = RenderStatus.PENDING


class Orchestrator:
    """
    Orchestrates multi-engine rendering pipeline.
    
    Routes scenes to appropriate engines based on type and complexity,
    manages dependencies, and assembles final output.
    """
    
    def __init__(self, 
                 remotion_config: Optional[Dict[str, Any]] = None,
                 ffmpeg_config: Optional[Dict[str, Any]] = None):
        """
        Initialize orchestrator.
        
        Args:
            remotion_config: Configuration for RemotionAdapter
            ffmpeg_config: Configuration for FFmpegAdapter
        """
        self.remotion_config = remotion_config or {}
        self.ffmpeg_config = ffmpeg_config or {}
        
        # Engine instances (lazy initialized)
        self._remotion_adapter: Optional[RemotionAdapter] = None
        self._ffmpeg_adapter: Optional[FFmpegAdapter] = None
        
        # Active jobs
        self._jobs: Dict[str, OrchestratedJob] = {}
        
        # Routing rules
        self._routing_rules = self._init_routing_rules()
    
    def _init_routing_rules(self) -> Dict[SceneType, EngineType]:
        """Initialize scene type to engine routing rules."""
        return {
            SceneType.TEXT_ANIMATION: EngineType.REMOTION,
            SceneType.MOTION_GRAPHICS: EngineType.REMOTION,
            SceneType.VIDEO_COMPOSITION: EngineType.FFMPEG,
            SceneType.TRANSITION: EngineType.FFMPEG,
            SceneType.EFFECT: EngineType.FFMPEG,
            SceneType.BACKGROUND: EngineType.REMOTION,
            SceneType.OVERLAY: EngineType.FFMPEG
        }
    
    def get_engine(self, engine_type: EngineType) -> BaseEngine:
        """
        Get or initialize engine adapter.
        
        Args:
            engine_type: Type of engine to get
            
        Returns:
            Engine adapter instance
        """
        if engine_type == EngineType.REMOTION:
            if not self._remotion_adapter:
                self._remotion_adapter = RemotionAdapter(**self.remotion_config)
                self._remotion_adapter.initialize()
            return self._remotion_adapter
            
        elif engine_type == EngineType.FFMPEG:
            if not self._ffmpeg_adapter:
                self._ffmpeg_adapter = FFmpegAdapter(**self.ffmpeg_config)
                self._ffmpeg_adapter.initialize()
            return self._ffmpeg_adapter
        
        raise ValueError(f"Unsupported engine type: {engine_type}")
    
    def route_scene(self, scene_config: Dict[str, Any]) -> EngineType:
        """
        Determine which engine should handle a scene.
        
        Args:
            scene_config: Scene configuration
            
        Returns:
            Appropriate engine type
        """
        # Check for explicit engine specification
        if "engine" in scene_config:
            engine_str = scene_config["engine"].upper()
            return EngineType[engine_str]
        
        # Infer from scene type
        scene_type_str = scene_config.get("type", "motion_graphics")
        try:
            scene_type = SceneType(scene_type_str)
            return self._routing_rules.get(scene_type, EngineType.REMOTION)
        except ValueError:
            # Default to Remotion for unknown types
            return EngineType.REMOTION
    
    def create_job(self, 
                   job_name: str,
                   scenes: List[Dict[str, Any]],
                   final_output_path: str,
                   **metadata) -> str:
        """
        Create an orchestrated rendering job from scene graph.
        
        Args:
            job_name: Name of the job
            scenes: List of scene configurations
            final_output_path: Path for final assembled output
            **metadata: Additional job metadata
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Parse scenes and create tasks
        tasks = self._parse_scenes_to_tasks(scenes)
        
        job = OrchestratedJob(
            id=job_id,
            name=job_name,
            tasks=tasks,
            final_output_path=final_output_path,
            metadata=metadata
        )
        
        self._jobs[job_id] = job
        
        return job_id
    
    def _parse_scenes_to_tasks(self, scenes: List[Dict[str, Any]]) -> List[SceneTask]:
        """
        Parse scene configurations into executable tasks.
        
        Args:
            scenes: List of scene configurations
            
        Returns:
            List of scene tasks
        """
        tasks = []
        
        for i, scene in enumerate(scenes):
            # Determine engine
            engine = self.route_scene(scene)
            
            # Determine scene type
            scene_type_str = scene.get("type", "motion_graphics")
            try:
                scene_type = SceneType(scene_type_str)
            except ValueError:
                scene_type = SceneType.MOTION_GRAPHICS
            
            # Determine dependencies (scenes must render in order by default)
            dependencies = []
            if i > 0:
                dependencies.append(tasks[i-1].id)
            
            # Add explicit dependencies if specified
            if "depends_on" in scene:
                dependencies.extend(scene["depends_on"])
            
            # Create task
            task_id = scene.get("id", f"task_{i}_{uuid.uuid4()}")
            output_path = scene.get("output_path", f"./tmp/{task_id}.mp4")
            
            task = SceneTask(
                id=task_id,
                scene_type=scene_type,
                engine=engine,
                config=scene,
                dependencies=dependencies,
                output_path=output_path
            )
            
            tasks.append(task)
        
        return tasks
    
    def execute_job(self, job_id: str) -> RenderResult:
        """
        Execute an orchestrated job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Final render result
        """
        job = self._jobs.get(job_id)
        if not job:
            return RenderResult(
                status=RenderStatus.FAILED,
                error=f"Job {job_id} not found"
            )
        
        job.status = RenderStatus.IN_PROGRESS
        
        try:
            # Execute tasks in dependency order
            completed_tasks = {}
            
            for task in job.tasks:
                # Wait for dependencies
                if not self._check_dependencies(task, completed_tasks):
                    return RenderResult(
                        status=RenderStatus.FAILED,
                        error=f"Dependencies not met for task {task.id}"
                    )
                
                # Execute task
                result = self._execute_task(task, completed_tasks)
                
                if result.status != RenderStatus.COMPLETED:
                    job.status = RenderStatus.FAILED
                    return result
                
                task.status = RenderStatus.COMPLETED
                task.result = result
                completed_tasks[task.id] = result
            
            # Assemble final output
            final_result = self._assemble_final_output(job, completed_tasks)
            
            job.status = final_result.status
            return final_result
            
        except Exception as e:
            job.status = RenderStatus.FAILED
            return RenderResult(
                status=RenderStatus.FAILED,
                error=str(e)
            )
    
    def _check_dependencies(self, 
                           task: SceneTask, 
                           completed_tasks: Dict[str, RenderResult]) -> bool:
        """
        Check if all task dependencies are completed.
        
        Args:
            task: Task to check
            completed_tasks: Dict of completed task results
            
        Returns:
            True if all dependencies are met
        """
        for dep_id in task.dependencies:
            if dep_id not in completed_tasks:
                return False
            if completed_tasks[dep_id].status != RenderStatus.COMPLETED:
                return False
        return True
    
    def _execute_task(self, 
                     task: SceneTask, 
                     completed_tasks: Dict[str, RenderResult]) -> RenderResult:
        """
        Execute a single scene task.
        
        Args:
            task: Task to execute
            completed_tasks: Dict of completed task results
            
        Returns:
            Task render result
        """
        # Get appropriate engine
        engine = self.get_engine(task.engine)
        
        # Prepare render config
        config = self._prepare_render_config(task, completed_tasks)
        
        # Add any assets or scenes to engine
        if "assets" in task.config:
            for asset in task.config["assets"]:
                engine.add_asset(**asset)
        
        if "scene" in task.config:
            engine.add_scene(task.config["scene"])
        
        # Execute render
        result = engine.render(config)
        
        # Cleanup engine state
        engine.cleanup()
        
        return result
    
    def _prepare_render_config(self, 
                               task: SceneTask,
                               completed_tasks: Dict[str, RenderResult]) -> RenderConfig:
        """
        Prepare render configuration for a task.
        
        Args:
            task: Task to prepare config for
            completed_tasks: Dict of completed task results
            
        Returns:
            Render configuration
        """
        config_dict = task.config.get("render", {})
        
        # Extract or use defaults
        width = config_dict.get("width", 1920)
        height = config_dict.get("height", 1080)
        fps = config_dict.get("fps", 30)
        quality = config_dict.get("quality", "high")
        format = config_dict.get("format", "mp4")
        codec = config_dict.get("codec")
        duration = config_dict.get("duration")
        
        return RenderConfig(
            output_path=task.output_path,
            width=width,
            height=height,
            fps=fps,
            quality=quality,
            format=format,
            codec=codec,
            duration=duration,
            additional_params=config_dict.get("additional_params", {})
        )
    
    def _assemble_final_output(self, 
                              job: OrchestratedJob,
                              completed_tasks: Dict[str, RenderResult]) -> RenderResult:
        """
        Assemble final output from all task results.
        
        Args:
            job: Job to assemble
            completed_tasks: Dict of completed task results
            
        Returns:
            Final render result
        """
        # Collect all intermediate outputs
        intermediate_files = []
        for task in job.tasks:
            if task.result and task.result.output_path:
                intermediate_files.append(task.result.output_path)
        
        if not intermediate_files:
            return RenderResult(
                status=RenderStatus.FAILED,
                error="No intermediate outputs to assemble"
            )
        
        # If only one output, just copy/rename it
        if len(intermediate_files) == 1:
            import shutil
            shutil.copy2(intermediate_files[0], job.final_output_path)
            return RenderResult(
                status=RenderStatus.COMPLETED,
                output_path=job.final_output_path
            )
        
        # Use FFmpeg to concatenate multiple outputs
        ffmpeg = self.get_engine(EngineType.FFMPEG)
        
        transition = job.metadata.get("transition", None)
        result = ffmpeg.concat_videos(
            input_files=intermediate_files,
            output_path=job.final_output_path,
            transition=transition
        )
        
        return result
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        job = self._jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        tasks_status = []
        for task in job.tasks:
            tasks_status.append({
                "id": task.id,
                "type": task.scene_type.value,
                "engine": task.engine.value,
                "status": task.status.value,
                "output": task.output_path
            })
        
        return {
            "job_id": job.id,
            "name": job.name,
            "status": job.status.value,
            "tasks": tasks_status,
            "final_output": job.final_output_path
        }
    
    def cleanup(self):
        """Cleanup all engine resources."""
        if self._remotion_adapter:
            self._remotion_adapter.cleanup()
            self._remotion_adapter = None
        
        if self._ffmpeg_adapter:
            self._ffmpeg_adapter.cleanup()
            self._ffmpeg_adapter = None
        
        self._jobs.clear()
