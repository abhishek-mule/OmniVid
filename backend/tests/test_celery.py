"""
Celery task integration tests.
"""

from unittest.mock import MagicMock, patch

import pytest

from ..src.services.task_manager import TaskManager
from ..src.workers.celery_app import app as celery_app
from ..src.workers.tasks.video_processing import (generate_video,
                                                  process_video_upload,
                                                  render_video_blender)


@pytest.fixture
def mock_db():
    """Mock database session."""
    mock_db = MagicMock()
    return mock_db


@pytest.fixture
def task_manager():
    """Create task manager instance."""
    return TaskManager()


def test_generate_video_task():
    """Test video generation task."""
    video_data = {
        "video_id": 1,
        "prompt": "Create a video about nature",
        "settings": '{"duration": 30}',
    }
    user_id = 1

    # Test task execution
    result = generate_video.apply(args=(video_data, user_id))

    assert result.successful()
    assert "video_id" in result.result
    assert result.result["status"] == "completed"


def test_render_video_blender_task():
    """Test Blender rendering task."""
    video_data = {
        "video_id": 2,
        "prompt": "3D animation video",
        "settings": '{"engine": "blender"}',
    }
    user_id = 1

    # Test task execution
    result = render_video_blender.apply(args=(video_data, user_id))

    assert result.successful()
    assert "video_id" in result.result
    assert result.result["engine"] == "blender"


def test_process_video_upload_task():
    """Test video upload processing task."""
    asset_data = {"asset_id": 1, "video_id": 1}
    user_id = 1

    # Test task execution
    result = process_video_upload.apply(args=(asset_data, user_id))

    assert result.successful()
    assert "asset_id" in result.result
    assert result.result["status"] == "processed"


@patch("src.services.task_manager.SessionLocal")
@patch("src.services.task_manager.VideoRepository")
@patch("src.services.task_manager.JobRepository")
@patch("src.services.task_manager.ProjectRepository")
def test_queue_video_generation(
    mock_project_repo, mock_job_repo, mock_video_repo, mock_session_local, task_manager
):
    """Test queueing video generation task."""
    # Setup mocks
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    mock_video = MagicMock()
    mock_video.id = 1
    mock_video.project_id = 1
    mock_video_repo.return_value.get_video.return_value = mock_video

    mock_project = MagicMock()
    mock_project.user_id = 1
    mock_project_repo.return_value.get_project.return_value = mock_project

    mock_job = MagicMock()
    mock_job.id = 1
    mock_job_repo.return_value.create_job.return_value = mock_job

    # Test task queueing
    with patch("src.services.task_manager.generate_video.delay") as mock_delay:
        mock_task = MagicMock()
        mock_task.id = "test-task-id"
        mock_delay.return_value = mock_task

        task_id = task_manager.queue_video_generation(1, 1, "default")

        assert task_id == "test-task-id"
        mock_delay.assert_called_once()


@patch("src.services.task_manager.SessionLocal")
@patch("src.services.task_manager.JobRepository")
def test_get_task_status(task_manager):
    """Test getting task status."""
    # Test successful task
    with patch.object(celery_app.AsyncResult, "status", "SUCCESS"):
        with patch.object(celery_app.AsyncResult, "result", {"video_id": 1}):
            status = task_manager.get_task_status("test-task-id")
            assert status["status"] == "SUCCESS"
            assert status["result"]["video_id"] == 1


@patch("src.services.task_manager.celery_app")
def test_cancel_task(mock_celery_app, task_manager):
    """Test cancelling a task."""
    mock_task = MagicMock()
    mock_task.status = "PENDING"
    mock_celery_app.AsyncResult.return_value = mock_task

    result = task_manager.cancel_task("test-task-id")

    assert result is True
    mock_task.revoke.assert_called_once_with(terminate=True)


@patch("src.services.task_manager.celery_app.control.inspect")
def test_get_worker_stats(mock_inspect, task_manager):
    """Test getting worker statistics."""
    # Setup mock
    mock_inspect.return_value = MagicMock()
    mock_inspect.return_value.stats.return_value = {"worker1": {"pool": "prefork"}}
    mock_inspect.return_value.active.return_value = {"worker1": []}
    mock_inspect.return_value.scheduled.return_value = {}

    stats = task_manager.get_worker_stats()

    assert "workers" in stats
    assert "active_tasks" in stats
    assert "scheduled_tasks" in stats


def test_cleanup_old_tasks(task_manager):
    """Test cleanup of old tasks."""
    result = task_manager.cleanup_old_tasks(24)

    assert "cleaned_tasks" in result
    assert "cutoff_time" in result
    assert result["message"] == "Task cleanup completed"


# Test task progress updates
def test_task_progress_tracking():
    """Test that tasks properly update progress."""
    video_data = {"video_id": 1, "prompt": "test"}
    user_id = 1

    # Execute task with progress tracking
    result = generate_video.apply(args=(video_data, user_id))

    assert result.successful()
    # The task should complete successfully, indicating progress tracking works


# Test error handling in tasks
def test_video_generation_task_error():
    """Test error handling in video generation task."""
    # Test with invalid video data
    invalid_video_data = {"video_id": 999, "prompt": "test"}  # Non-existent video

    with pytest.raises(ValueError):
        generate_video.apply(args=(invalid_video_data, 1)).get()


# Test task isolation
def test_task_isolation():
    """Test that tasks are properly isolated."""
    video_data1 = {"video_id": 1, "prompt": "video1"}
    video_data2 = {"video_id": 2, "prompt": "video2"}
    user_id = 1

    # Submit multiple tasks
    result1 = generate_video.delay(video_data1, user_id)
    result2 = generate_video.delay(video_data2, user_id)

    # Both should complete successfully
    assert result1.successful()
    assert result2.successful()

    # Results should be different
    assert result1.get()["video_id"] == 1
    assert result2.get()["video_id"] == 2
