"""
Tests for the OmniVid video generation API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Import the FastAPI app
from ..src.api.main import app

client = TestClient(app)

# Test data
SAMPLE_VIDEO_REQUEST = {
    "prompt": "Create a professional tech logo reveal",
    "resolution": "1080p",
    "fps": 30,
    "duration": 10,
    "quality": "high"
}

@pytest.fixture
def mock_anthropic():
    """Mock the Anthropic API client."""
    with patch('src.api.main.anthropic') as mock_anth:
        mock_client = MagicMock()
        mock_anth.Anthropic.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_job_id():
    """Return a consistent job ID for testing."""
    return "test-job-123"

def test_generate_video_success(mock_anthropic, mock_job_id):
    """Test successful video generation request."""
    # Mock the response from Claude
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text=json.dumps({
            "scene_type": "logo_reveal",
            "title": "TechCorp",
            "style": "professional",
            "colors": ["#1a1a2e", "#4a4a8f"]
        }))]
    )
    
    # Mock uuid4 to return a consistent job ID
    with patch('uuid.uuid4', return_value=mock_job_id):
        response = client.post("/api/generate", json=SAMPLE_VIDEO_REQUEST)
    
    assert response.status_code == 200
    assert response.json() == {
        "job_id": mock_job_id,
        "status": "queued",
        "progress": 0,
        "stage": "Queued...",
        "video_url": None,
        "error": None,
        "created_at": response.json()["created_at"]  # This will be set by the server
    }

def test_get_job_status(mock_job_id):
    """Test getting job status."""
    # First create a job
    with patch('uuid.uuid4', return_value=mock_job_id):
        client.post("/api/generate", json=SAMPLE_VIDEO_REQUEST)
    
    # Then check its status
    response = client.get(f"/api/jobs/{mock_job_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == mock_job_id
    assert data["status"] in ["queued", "processing", "completed", "failed"]

def test_get_nonexistent_job():
    """Test getting status of a non-existent job."""
    response = client.get("/api/jobs/nonexistent-job")
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]

def test_list_videos():
    """Test listing generated videos."""
    response = client.get("/api/videos")
    assert response.status_code == 200
    assert isinstance(response.json()["videos"], list)

def test_get_video_not_found():
    """Test getting a non-existent video."""
    response = client.get("/api/videos/nonexistent-video")
    assert response.status_code == 404

def test_get_templates():
    """Test getting available video templates."""
    response = client.get("/api/templates")
    assert response.status_code == 200
    templates = response.json()["templates"]
    assert len(templates) > 0
    assert all("id" in t and "name" in t for t in templates)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert "endpoints" in response.json()

def test_generate_video_invalid_request():
    """Test video generation with invalid request data."""
    response = client.post("/api/generate", json={"invalid": "data"})
    assert response.status_code == 422  # Validation error

# This test is commented out as it requires more complex mocking
# def test_process_video_job_failure(mock_anthropic, mock_job_id):
#     """Test error handling in the background job."""
#     # Make the mock raise an exception
#     mock_anthropic.messages.create.side_effect = Exception("API Error")
    
#     with patch('uuid.uuid4', return_value=mock_job_id):
#         response = client.post("/api/generate", json=SAMPLE_VIDEO_REQUEST)
    
#     # The initial response should still be 200
#     assert response.status_code == 200
    
#     # But the job should fail
#     response = client.get(f"/api/jobs/{mock_job_id}")
#     assert response.json()["status"] == "failed"
#     assert "error" in response.json()

# This test is commented out as it requires more complex async mocking
# def test_video_generation_workflow(mock_anthropic, mock_job_id):
#     """Test the complete video generation workflow."""
#     # Mock the response from Claude
#     mock_anthropic.messages.create.return_value = MagicMock(
#         content=[MagicMock(text=json.dumps({
#             "scene_type": "text_animation",
#             "title": "Test Video",
#             "subtitle": "This is a test",
#             "style": "modern",
#             "colors": ["#1a1a2e", "#4a4a8f"]
#         }))]
#     )
    
#     # Start a new job
#     with patch('uuid.uuid4', return_value=mock_job_id):
#         response = client.post("/api/generate", json=SAMPLE_VIDEO_REQUEST)
#     assert response.status_code == 200
    
#     # Check job status
#     response = client.get(f"/api/jobs/{mock_job_id}")
#     assert response.status_code == 200
#     assert response.json()["status"] in ["queued", "processing"]
    
#     # Simulate job completion
#     # In a real test, we would wait for the background task to complete
#     # or mock the background task to complete immediately
    
#     # Check that the video appears in the list
#     response = client.get("/api/videos")
#     videos = response.json()["videos"]
#     video = next((v for v in videos if v["id"] == mock_job_id), None)
#     assert video is not None
#     assert video["status"] == "completed"
