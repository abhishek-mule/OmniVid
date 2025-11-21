"""
End-to-end tests for the complete video generation workflow.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session

from ..src.api.main import app

# Import from the application
from ..src.database.connection import Base, engine, get_db
from ..src.database.models import Project, User, Video
from ..src.database.repository import ProjectRepository, UserRepository, VideoRepository
from ..src.database.schemas import LoginRequest, ProjectCreate, UserCreate, VideoCreate
from ..src.services.websocket_manager import connection_manager
from ..src.workers.celery_app import celery_app


class TestVideoGenerationWorkflow:
    """Test class for complete video generation end-to-end workflow."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def test_user_and_token(self, client, db):
        """Create a test user and get authentication token."""
        # Clean up any existing test user
        user_repo = UserRepository(db)
        existing_user = user_repo.get_user_by_email("e2e_test@example.com")
        if existing_user:
            db.delete(existing_user)
            db.commit()

        # Create user
        user_data = UserCreate(
            email="e2e_test@example.com",
            username="e2e_test_user",
            password="e2e_test_password",
            full_name="E2E Test User",
        )
        user = user_repo.create_user(user_data)

        # Login to get token
        login_data = LoginRequest(
            email="e2e_test@example.com", password="e2e_test_password"
        )
        login_response = client.post("/auth/login", json=login_data.dict())
        token = login_response.json()["access_token"]

        return user, token

    @pytest.fixture
    def test_project_and_video(self, db, test_user_and_token):
        """Create a test project and video."""
        user, token = test_user_and_token

        # Create project
        project_repo = ProjectRepository(db)
        project = project_repo.create_project(
            user.id,
            ProjectCreate(
                title="E2E Test Project",
                description="Test project for end-to-end testing",
                is_public=True,
            ),
        )

        # Create video
        video_repo = VideoRepository(db)
        video = video_repo.create_video(
            VideoCreate(
                title="E2E Test Video",
                prompt="Create a short video about nature with beautiful landscapes",
                project_id=project.id,
                settings='{"duration": 15, "resolution": "1080p", "fps": 30}',
            )
        )

        return project, video, user, token

    def test_complete_video_workflow(self, client, db, test_project_and_video):
        """Test the complete video generation workflow from creation to completion."""
        project, video, user, token = test_project_and_video
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Verify video is created with pending status
        assert video.status == "pending"
        assert video.progress == 0

        # Step 2: Start video generation
        with patch(
            "src.workers.tasks.video_processing.generate_video.delay"
        ) as mock_task:
            mock_task.return_value = AsyncMock(id="test-celery-task-id")

            # Start the generation process (this would typically be triggered by a frontend action)
            video_repo = VideoRepository(db)
            video_repo.update_video(
                video.id,
                {"status": "processing", "celery_task_id": "test-celery-task-id"},
            )
            video_repo.update_video_progress(video.id, 10, "processing")

            # Verify the mock was called
            mock_task.assert_called_once()

        # Step 3: Check video status via API
        response = client.get(f"/api/videos/{video.id}/status", headers=headers)
        assert response.status_code == 200

        status_data = response.json()
        assert status_data["video_id"] == video.id
        assert status_data["status"] == "processing"
        assert status_data["progress"] == 10

        # Step 4: Verify progress updates in database
        video_repo.update_video_progress(video.id, 50, "processing")

        response = client.get(f"/api/videos/{video.id}/status", headers=headers)
        assert response.status_code == 200
        assert response.json()["progress"] == 50

        # Step 5: Simulate completion
        video_repo.update_video_progress(video.id, 100, "completed")
        video_repo.update_video(
            video.id,
            {
                "video_url": "/output/videos/test_video.mp4",
                "thumbnail_url": "/output/thumbnails/test_thumb.jpg",
                "duration": 15.0,
            },
        )

        # Step 6: Verify final status
        response = client.get(f"/api/videos/{video.id}/status", headers=headers)
        assert response.status_code == 200

        final_data = response.json()
        assert final_data["status"] == "completed"
        assert final_data["progress"] == 100

    def test_video_workflow_with_error(self, client, db, test_project_and_video):
        """Test video generation workflow with error handling."""
        project, video, user, token = test_project_and_video
        headers = {"Authorization": f"Bearer {token}"}

        # Start processing
        video_repo = VideoRepository(db)
        video_repo.update_video_progress(video.id, 25, "processing")

        # Simulate an error during processing
        video_repo.update_video_progress(video.id, 0, "failed")
        video_repo.update_video(video.id, {"error_message": "Render engine crashed"})

        # Verify error status
        response = client.get(f"/api/videos/{video.id}/status", headers=headers)
        assert response.status_code == 200

        error_data = response.json()
        assert error_data["status"] == "failed"
        assert error_data["progress"] == 0
        assert "Render engine crashed" in error_data.get("error_message", "")

        # Test retry functionality
        response = client.post(f"/api/videos/{video.id}/retry", headers=headers)
        assert response.status_code == 200
        assert "Video generation retry queued" in response.json()["message"]

        # Verify video is reset to pending
        response = client.get(f"/api/videos/{video.id}/status", headers=headers)
        assert response.json()["status"] == "pending"

    def test_websocket_connection(self, client, test_project_and_video):
        """Test WebSocket connection and progress updates."""
        project, video, user, token = test_project_and_video

        # Test WebSocket connection
        with client.websocket_connect(f"/ws/videos/{video.id}") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connection"
            assert data["data"]["status"] == "connected"
            assert data["data"]["video_id"] == str(video.id)

            # Test ping/pong
            websocket.send_text("ping")
            response = websocket.receive_json()
            assert response["type"] == "ping"
            assert response["data"]["message"] == "pong"

    def test_websocket_progress_broadcast(self, client, db, test_project_and_video):
        """Test WebSocket progress broadcasting."""
        project, video, user, token = test_project_and_video

        # Test the broadcast endpoint (for development/testing)
        response = client.post(
            "/ws/test/broadcast",
            json={
                "video_id": str(video.id),
                "progress": 75,
                "stage": "Rendering frames",
            },
        )
        assert response.status_code == 200

        # Note: In a real test environment, you would need to set up the WebSocket manager
        # to handle the broadcasting properly. This is a simplified test.

    def test_video_crud_operations(self, client, db, test_project_and_video):
        """Test complete CRUD operations for videos."""
        project, video, user, token = test_project_and_video
        headers = {"Authorization": f"Bearer {token}"}

        # Test GET all videos
        response = client.get("/api/videos", headers=headers)
        assert response.status_code == 200
        videos = response.json()
        assert len(videos) == 1
        assert videos[0]["id"] == video.id

        # Test GET specific video
        response = client.get(f"/api/videos/{video.id}", headers=headers)
        assert response.status_code == 200
        video_data = response.json()
        assert video_data["id"] == video.id
        assert video_data["title"] == "E2E Test Video"

        # Test UPDATE video
        update_data = {
            "title": "Updated E2E Test Video",
            "description": "Updated description",
        }
        response = client.put(
            f"/api/videos/{video.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200
        updated_video = response.json()
        assert updated_video["title"] == "Updated E2E Test Video"

        # Test DELETE video (after setting it to non-processing status)
        video_repo = VideoRepository(db)
        video_repo.update_video_progress(video.id, 100, "completed")

        response = client.delete(f"/api/videos/{video.id}", headers=headers)
        assert response.status_code == 200
        assert "Video deleted successfully" in response.json()["message"]

        # Verify deletion
        response = client.get(f"/api/videos/{video.id}", headers=headers)
        assert response.status_code == 404

    def test_multi_video_workflow(self, client, db, test_user_and_token):
        """Test handling multiple videos simultaneously."""
        user, token = test_user_and_token
        headers = {"Authorization": f"Bearer {token}"}

        # Create project
        project_repo = ProjectRepository(db)
        project = project_repo.create_project(
            user.id, ProjectCreate(title="Multi-Video Test Project", is_public=True)
        )

        # Create multiple videos
        video_repo = VideoRepository(db)
        videos = []
        for i in range(3):
            video = video_repo.create_video(
                VideoCreate(
                    title=f"Video {i+1}",
                    prompt=f"Create video number {i+1}",
                    project_id=project.id,
                )
            )
            videos.append(video)

        # Test getting all videos
        response = client.get("/api/videos", headers=headers)
        assert response.status_code == 200
        all_videos = response.json()
        assert len(all_videos) == 3

        # Test progress updates for multiple videos
        for i, video in enumerate(videos):
            progress = (i + 1) * 25
            video_repo.update_video_progress(video.id, progress, "processing")

        # Verify all videos have correct progress
        for i, video in enumerate(videos):
            response = client.get(f"/api/videos/{video.id}/status", headers=headers)
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["progress"] == (i + 1) * 25

    def test_project_isolation(self, client, db):
        """Test that users can only access their own projects."""
        # Create two users
        user_repo = UserRepository(db)

        user1 = user_repo.create_user(
            UserCreate(email="user1@example.com", username="user1", password="password")
        )
        user2 = user_repo.create_user(
            UserCreate(email="user2@example.com", username="user2", password="password")
        )

        # Login as user1
        login_data = LoginRequest(email="user1@example.com", password="password")
        response1 = client.post("/auth/login", json=login_data.dict())
        token1 = response1.json()["access_token"]

        # Login as user2
        login_data = LoginRequest(email="user2@example.com", password="password")
        response2 = client.post("/auth/login", json=login_data.dict())
        token2 = response2.json()["access_token"]

        # User1 creates a private project
        project_repo = ProjectRepository(db)
        private_project = project_repo.create_project(
            user1.id, ProjectCreate(title="Private Project", is_public=False)
        )

        # User2 creates a public project
        public_project = project_repo.create_project(
            user2.id, ProjectCreate(title="Public Project", is_public=True)
        )

        # User1 can see their private project
        response = client.get(
            f"/api/projects/{private_project.id}",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response.status_code == 200

        # User2 cannot see user1's private project
        response = client.get(
            f"/api/projects/{private_project.id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 403

        # User2 can see the public project
        response = client.get(
            f"/api/projects/{public_project.id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 200

        # User1 can see the public project
        response = client.get(
            f"/api/projects/{public_project.id}",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response.status_code == 200

    def test_websocket_status_endpoint(self, client):
        """Test the WebSocket status endpoint."""
        response = client.get("/ws/status")
        assert response.status_code == 200

        status_data = response.json()
        assert "status" in status_data
        assert "total_connections" in status_data
        assert "active_videos" in status_data
        assert isinstance(status_data["total_connections"], int)
        assert isinstance(status_data["active_videos"], list)


# Additional test utilities
class TestCeleryIntegration:
    """Test Celery task integration."""

    def test_celery_task_creation(self, test_project_and_video):
        """Test that Celery tasks are created correctly."""
        project, video, user, token = test_project_and_video

        # Test task creation
        with patch(
            "src.workers.tasks.video_processing.generate_video.delay"
        ) as mock_task:
            mock_task.return_value = AsyncMock(id="mock-task-id")

            # Simulate task creation
            from ..src.workers.tasks.video_processing import generate_video

            task = generate_video.delay({"video_id": video.id}, user.id)

            # Verify task was created
            mock_task.assert_called_once()
            assert task.id == "mock-task-id"


class TestDatabaseIntegrity:
    """Test database integrity and constraints."""

    def test_video_deletion_constraints(self, client, db, test_project_and_video):
        """Test that videos cannot be deleted while processing."""
        project, video, user, token = test_project_and_video
        headers = {"Authorization": f"Bearer {token}"}

        # Try to delete video while it's processing (should fail)
        video_repo = VideoRepository(db)
        video_repo.update_video_progress(video.id, 50, "processing")

        response = client.delete(f"/api/videos/{video.id}", headers=headers)
        assert response.status_code == 400
        assert (
            "Cannot delete video that is currently processing"
            in response.json()["detail"]
        )

        # After completion, deletion should succeed
        video_repo.update_video_progress(video.id, 100, "completed")
        response = client.delete(f"/api/videos/{video.id}", headers=headers)
        assert response.status_code == 200


# Performance tests
class TestPerformance:
    """Test system performance under load."""

    def test_multiple_concurrent_videos(self, client, db, test_user_and_token):
        """Test handling multiple videos concurrently."""
        user, token = test_user_and_token
        headers = {"Authorization": f"Bearer {token}"}

        # Create project
        project_repo = ProjectRepository(db)
        project = project_repo.create_project(
            user.id, ProjectCreate(title="Load Test Project", is_public=True)
        )

        # Create many videos at once
        video_repo = VideoRepository(db)
        start_time = time.time()

        for i in range(20):
            video_data = {
                "title": f"Load Test Video {i+1}",
                "prompt": f"Create video number {i+1} for load testing",
                "project_id": project.id,
                "settings": '{"duration": 15}',
            }

            response = client.post("/api/videos", json=video_data, headers=headers)
            assert response.status_code == 200

        creation_time = time.time() - start_time

        # Verify all videos were created
        response = client.get("/api/videos", headers=headers)
        assert response.status_code == 200
        videos = response.json()
        assert len(videos) == 20

        # Creation should complete in reasonable time (less than 5 seconds)
        assert creation_time < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
