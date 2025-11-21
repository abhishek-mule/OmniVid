"""
API endpoint tests for projects and videos.
"""

import pytest
from fastapi.testclient import TestClient

from ..src.api.main import app
from ..src.database.connection import Base, engine
from ..src.database.models import Project, User, Video
from ..src.database.repository import (ProjectRepository, UserRepository,
                                       VideoRepository)
from ..src.database.schemas import (LoginRequest, ProjectCreate, UserCreate,
                                    VideoCreate)

client = TestClient(app)


@pytest.fixture
def test_user_and_token(db):
    """Create a test user and get authentication token."""
    # Create user
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User",
    )
    user = user_repo.create_user(user_data)

    # Login to get token
    login_data = LoginRequest(email="test@example.com", password="testpassword")
    login_response = client.post("/auth/login", json=login_data.dict())
    token = login_response.json()["access_token"]

    return user, token


# Project tests
def test_create_project(db, test_user_and_token):
    """Test creating a new project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    project_data = {
        "title": "Test Project",
        "description": "A test project description",
        "is_public": True,
    }

    response = client.post("/api/projects", json=project_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Project"
    assert data["description"] == "A test project description"
    assert data["is_public"] is True
    assert data["user_id"] == user.id


def test_get_projects(db, test_user_and_token):
    """Test getting user projects."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create some projects
    project_repo = ProjectRepository(db)
    project1 = project_repo.create_project(
        user.id, ProjectCreate(title="Project 1", is_public=True)
    )
    project2 = project_repo.create_project(
        user.id, ProjectCreate(title="Project 2", is_public=False)
    )

    response = client.get("/api/projects", headers=headers)

    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 2
    assert projects[0]["title"] == "Project 1"
    assert projects[1]["title"] == "Project 2"


def test_get_project_by_id(db, test_user_and_token):
    """Test getting a specific project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a project
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    response = client.get(f"/api/projects/{project.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project.id
    assert data["title"] == "Test Project"


def test_get_nonexistent_project(db, test_user_and_token):
    """Test getting a project that doesn't exist."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/projects/999", headers=headers)

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_update_project(db, test_user_and_token):
    """Test updating a project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a project
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Original Title", is_public=True)
    )

    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "is_public": False,
    }

    response = client.put(
        f"/api/projects/{project.id}", json=update_data, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["is_public"] is False


def test_delete_project(db, test_user_and_token):
    """Test deleting a project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a project
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    response = client.delete(f"/api/projects/{project.id}", headers=headers)

    assert response.status_code == 200
    assert "Project deleted successfully" in response.json()["message"]

    # Verify project is deleted
    response = client.get(f"/api/projects/{project.id}", headers=headers)
    assert response.status_code == 404


# Video tests
def test_create_video(db, test_user_and_token):
    """Test creating a new video."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a project first
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    video_data = {
        "title": "Test Video",
        "description": "A test video",
        "prompt": "Create a video about cats",
        "project_id": project.id,
        "settings": '{"duration": 30}',
    }

    response = client.post("/api/videos", json=video_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Video"
    assert data["prompt"] == "Create a video about cats"
    assert data["project_id"] == project.id
    assert data["status"] == "pending"


def test_create_video_with_invalid_project(db, test_user_and_token):
    """Test creating a video with an invalid project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    video_data = {
        "title": "Test Video",
        "prompt": "Create a video",
        "project_id": 999,  # Invalid project
    }

    response = client.post("/api/videos", json=video_data, headers=headers)

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_get_videos(db, test_user_and_token):
    """Test getting user videos."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a project and videos
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    video_repo = VideoRepository(db)
    video1 = video_repo.create_video(
        VideoCreate(title="Video 1", prompt="First video", project_id=project.id)
    )
    video2 = video_repo.create_video(
        VideoCreate(title="Video 2", prompt="Second video", project_id=project.id)
    )

    response = client.get("/api/videos", headers=headers)

    assert response.status_code == 200
    videos = response.json()
    assert len(videos) == 2
    assert videos[0]["title"] == "Video 1"
    assert videos[1]["title"] == "Video 2"


def test_get_video_by_id(db, test_user_and_token):
    """Test getting a specific video."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create project and video
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    video_repo = VideoRepository(db)
    video = video_repo.create_video(
        VideoCreate(title="Test Video", prompt="Test prompt", project_id=project.id)
    )

    response = client.get(f"/api/videos/{video.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == video.id
    assert data["title"] == "Test Video"


def test_get_video_status(db, test_user_and_token):
    """Test getting video status."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create project and video
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    video_repo = VideoRepository(db)
    video = video_repo.create_video(
        VideoCreate(title="Test Video", prompt="Test prompt", project_id=project.id)
    )

    # Update video progress
    video_repo.update_video_progress(video.id, 50, "processing")

    response = client.get(f"/api/videos/{video.id}/status", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["video_id"] == video.id
    assert data["status"] == "processing"
    assert data["progress"] == 50


def test_retry_failed_video(db, test_user_and_token):
    """Test retrying a failed video generation."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create project and video
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user.id, ProjectCreate(title="Test Project", is_public=True)
    )

    video_repo = VideoRepository(db)
    video = video_repo.create_video(
        VideoCreate(title="Test Video", prompt="Test prompt", project_id=project.id)
    )

    # Mark video as failed
    video_repo.update_video_progress(video.id, 0, "failed")
    video_repo.update_video(video.id, {"error_message": "Render engine error"})

    # Retry video
    response = client.post(f"/api/videos/{video.id}/retry", headers=headers)

    assert response.status_code == 200
    assert "Video generation retry queued" in response.json()["message"]


# Permission tests
def test_create_video_without_permission(db):
    """Test creating a video in a project the user doesn't own."""
    # Create two users
    user_repo = UserRepository(db)
    user1 = user_repo.create_user(
        UserCreate(email="user1@example.com", username="user1", password="password")
    )
    user2 = user_repo.create_user(
        UserCreate(email="user2@example.com", username="user2", password="password")
    )

    # Login as user2
    login_data = LoginRequest(email="user2@example.com", password="password")
    login_response = client.post("/auth/login", json=login_data.dict())
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create project as user1
    project_repo = ProjectRepository(db)
    project = project_repo.create_project(
        user1.id, ProjectCreate(title="User1 Project", is_public=False)
    )

    # Try to create video in user1's project as user2
    video_data = {
        "title": "Unauthorized Video",
        "prompt": "Test prompt",
        "project_id": project.id,
    }

    response = client.post("/api/videos", json=video_data, headers=headers)

    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_access_public_project(db, test_user_and_token):
    """Test accessing a public project."""
    user, token = test_user_and_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create another user and a public project
    user_repo = UserRepository(db)
    other_user = user_repo.create_user(
        UserCreate(email="other@example.com", username="otheruser", password="password")
    )

    project_repo = ProjectRepository(db)
    public_project = project_repo.create_project(
        other_user.id, ProjectCreate(title="Public Project", is_public=True)
    )

    # Should be able to access public project
    response = client.get(f"/api/projects/{public_project.id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Public Project"
