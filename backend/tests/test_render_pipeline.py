"""
Render pipeline integration tests.
"""

import os
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

from ..src.render_engines.base import (RenderEngineManager, RenderEngineType,
                                       RenderResult, RenderStatus)
from ..src.services.render_pipeline import RenderPipelineService


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def render_pipeline():
    """Create render pipeline service instance."""
    return RenderPipelineService()


def test_render_pipeline_initialization(render_pipeline):
    """Test render pipeline initialization."""
    # Check that engines are initialized
    available_engines = render_pipeline.get_available_engines()
    assert isinstance(available_engines, list)

    # Check that render manager is set up
    assert render_pipeline.render_manager is not None
    assert isinstance(render_pipeline.active_renders, dict)


@patch("src.render_engines.blender.engine.BlenderRenderEngine.initialize")
@patch("src.render_engines.ffmpeg.engine.FfmpegRenderEngine.initialize")
def test_engine_suggestion(mock_ffmpeg_init, mock_blender_init, render_pipeline):
    """Test engine suggestion based on prompt."""
    # Mock engines as available
    mock_blender_init.return_value = True
    mock_ffmpeg_init.return_value = True

    # Test math prompt
    math_prompt = "Create an animated equation showing the quadratic formula"
    suggested_engine = render_pipeline.suggest_engine(math_prompt, {})
    assert suggested_engine == RenderEngineType.MANIM

    # Test 3D prompt
    three_d_prompt = "Create a rotating 3D cube with lighting"
    suggested_engine = render_pipeline.suggest_engine(three_d_prompt, {})
    assert suggested_engine == RenderEngineType.BLENDER

    # Test web prompt
    web_prompt = "Create a React component animation for a landing page"
    suggested_engine = render_pipeline.suggest_engine(web_prompt, {})
    assert suggested_engine == RenderEngineType.REMOTION

    # Test general prompt (should default to FFmpeg)
    general_prompt = "Create a simple video with text and background music"
    suggested_engine = render_pipeline.suggest_engine(general_prompt, {})
    assert suggested_engine == RenderEngineType.FFMPEG


@patch("src.services.render_pipeline.RenderPipelineService.initialize_engines")
def test_get_available_engines(mock_init, render_pipeline, temp_output_dir):
    """Test getting available engines."""
    # Mock engines as available
    with patch.object(
        render_pipeline,
        "get_available_engines",
        return_value=[
            {"name": "Blender", "available": True, "version": "3.0.0"},
            {"name": "FFmpeg", "available": True, "version": "4.0.0"},
        ],
    ):
        engines = render_pipeline.get_available_engines()
        assert len(engines) == 2
        assert any(engine["name"] == "Blender" for engine in engines)
        assert any(engine["name"] == "FFmpeg" for engine in engines)


def test_start_render_job(render_pipeline, temp_output_dir):
    """Test starting a render job."""
    prompt = "Create a simple blue video"
    settings = {"resolution": (1920, 1080), "duration": 5, "fps": 30}
    output_path = os.path.join(temp_output_dir, "test_video.mp4")

    # Mock the render execution to avoid actual rendering
    with patch.object(render_pipeline, "_execute_render_job") as mock_execute:
        job_id = render_pipeline.start_render(prompt, settings, output_path)

        assert job_id is not None
        assert job_id in render_pipeline.active_renders
        mock_execute.assert_called_once()


def test_get_render_status(render_pipeline, temp_output_dir):
    """Test getting render job status."""
    # Add a mock job to the render manager
    job_id = "test-job-123"
    mock_job_data = {
        "job_id": job_id,
        "engine_type": "blender",
        "status": "pending",
        "progress": 0,
        "prompt": "Test prompt",
    }

    with patch.object(
        render_pipeline.render_manager, "get_job_status", return_value=mock_job_data
    ):
        status = render_pipeline.get_render_status(job_id)
        assert status is not None
        assert status["job_id"] == job_id
        assert status["status"] == "pending"


def test_cancel_render_job(render_pipeline):
    """Test cancelling a render job."""
    job_id = "test-job-123"

    with patch.object(render_pipeline.render_manager, "cancel_job", return_value=True):
        result = render_pipeline.cancel_render(job_id)
        assert result is True

        # Job should be removed from active renders
        assert job_id not in render_pipeline.active_renders


def test_get_all_render_jobs(render_pipeline):
    """Test getting all render jobs."""
    mock_jobs = [
        {"job_id": "job1", "status": "completed"},
        {"job_id": "job2", "status": "failed"},
    ]

    with patch.object(
        render_pipeline.render_manager, "get_all_jobs", return_value=mock_jobs
    ):
        jobs = render_pipeline.get_all_render_jobs()
        assert len(jobs) == 2
        assert jobs[0]["job_id"] == "job1"
        assert jobs[1]["job_id"] == "job2"


def test_get_render_statistics(render_pipeline):
    """Test getting render statistics."""
    # Mock completed jobs
    mock_completed = {
        "job1": Mock(engine_type=RenderEngineType.BLENDER),
        "job2": Mock(engine_type=RenderEngineType.FFMPEG),
        "job3": Mock(engine_type=RenderEngineType.BLENDER),
    }
    render_pipeline.render_manager.completed_jobs = mock_completed

    # Add active render
    render_pipeline.active_renders["job4"] = {}

    with patch.object(render_pipeline, "get_available_engines", return_value=[]):
        stats = render_pipeline.get_render_statistics()

        assert stats["active_renders"] == 1
        assert stats["total_completed"] == 3
        assert stats["total_jobs"] == 4
        assert "engine_usage" in stats
        assert stats["engine_usage"]["blender"] == 2
        assert stats["engine_usage"]["ffmpeg"] == 1


def test_cleanup_old_jobs(render_pipeline):
    """Test cleaning up old completed jobs."""
    with patch.object(
        render_pipeline.render_manager, "cleanup_completed_jobs", return_value=5
    ):
        cleaned = render_pipeline.cleanup_old_jobs(24)
        assert cleaned == 5


# Test render engine manager
def test_render_engine_manager():
    """Test render engine manager functionality."""
    manager = RenderEngineManager()

    # Test job creation
    job = manager.create_render_job(
        "test-job",
        RenderEngineType.FFMPEG,
        "Test prompt",
        {"resolution": (1920, 1080)},
        "/tmp/output.mp4",
    )

    assert job is not None
    assert job.job_id == "test-job"
    assert job.engine_type == RenderEngineType.FFMPEG
    assert "test-job" in manager.active_jobs


def test_render_result():
    """Test RenderResult class."""
    # Test successful result
    result = RenderResult(
        success=True, video_url="/tmp/video.mp4", duration=30.0, resolution=(1920, 1080)
    )

    assert result.success is True
    assert result.video_url == "/tmp/video.mp4"
    assert result.duration == 30.0
    assert result.resolution == (1920, 1080)
    assert result.error_message is None

    # Test failed result
    error_result = RenderResult(success=False, error_message="Render failed")

    assert error_result.success is False
    assert error_result.error_message == "Render failed"
    assert error_result.video_url is None


def test_render_status_enum():
    """Test RenderStatus enum values."""
    assert RenderStatus.PENDING.value == "pending"
    assert RenderStatus.INITIALIZING.value == "initializing"
    assert RenderStatus.RENDERING.value == "rendering"
    assert RenderStatus.COMPLETED.value == "completed"
    assert RenderStatus.FAILED.value == "failed"


def test_render_engine_type_enum():
    """Test RenderEngineType enum values."""
    assert RenderEngineType.BLENDER.value == "blender"
    assert RenderEngineType.FFMPEG.value == "ffmpeg"
    assert RenderEngineType.MANIM.value == "manim"
    assert RenderEngineType.REMOTION.value == "remotion"


# Test error handling
def test_start_render_with_invalid_engine(render_pipeline):
    """Test starting render with unavailable engine."""
    prompt = "Test prompt"
    settings = {"resolution": (1920, 1080)}
    output_path = "/tmp/test.mp4"

    with patch.object(
        render_pipeline.render_manager, "get_available_engines", return_value=[]
    ):
        with pytest.raises(ValueError, match="Engine .* is not available"):
            render_pipeline.start_render(
                prompt, settings, output_path, engine_type=RenderEngineType.BLENDER
            )


def test_start_render_with_invalid_settings(render_pipeline, temp_output_dir):
    """Test starting render with invalid settings."""
    prompt = "Test prompt"
    settings = {"invalid_setting": "invalid_value"}  # Invalid settings
    output_path = os.path.join(temp_output_dir, "test.mp4")

    with patch.object(render_pipeline, "render_manager") as mock_manager:
        mock_manager.get_available_engines.return_value = [RenderEngineType.BLENDER]
        mock_manager.validate_engine_settings.return_value = False

        with pytest.raises(ValueError, match="Invalid settings"):
            render_pipeline.start_render(
                prompt, settings, output_path, engine_type=RenderEngineType.BLENDER
            )


# Test engine selection with edge cases
def test_engine_selection_edge_cases(render_pipeline):
    """Test engine selection with edge case prompts."""
    # Empty prompt
    suggested = render_pipeline.suggest_engine("", {})
    assert suggested == RenderEngineType.FFMPEG  # Default fallback

    # Mixed keywords (should prioritize based on order)
    mixed_prompt = "3D math equation in React component"
    suggested = render_pipeline.suggest_engine(mixed_prompt, {})
    # Should pick first matching keyword (3D -> Blender)
    assert suggested == RenderEngineType.BLENDER

    # Very long prompt
    long_prompt = "create a comprehensive 3D animated visualization of mathematical functions using react components for a web interface"
    suggested = render_pipeline.suggest_engine(long_prompt, {})
    # Should pick first keyword (3D -> Blender)
    assert suggested == RenderEngineType.BLENDER
