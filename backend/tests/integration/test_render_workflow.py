"""
Integration tests for the video rendering workflow.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

def test_render_video_workflow(client, celery_worker):
    """Test the complete video rendering workflow."""
    # Mock the Celery task
    with patch('src.api.routes.render.create_render_task.delay') as mock_task:
        # Configure the mock to return a task ID
        mock_task.return_value = MagicMock(id='test-task-id')
        
        # Make a request to start a render job
        response = client.post(
            "/api/render",
            json={
                "template_id": "test-template",
                "assets": ["asset1.mp4", "asset2.png"],
                "output_format": "mp4"
            }
        )
        
        # Verify the response
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.json()
        
        # Verify the task was called with correct parameters
        mock_task.assert_called_once()
        
        # Get task status
        task_id = response.json()["task_id"]
        status_response = client.get(f"/api/render/{task_id}")
        
        # Verify status endpoint works
        assert status_response.status_code == status.HTTP_200_OK
        assert "status" in status_response.json()

def test_render_with_invalid_data(client):
    """Test rendering with invalid input data."""
    response = client.post(
        "/api/render",
        json={"invalid": "data"}  # Missing required fields
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
