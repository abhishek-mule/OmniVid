"""
Race condition and concurrency tests for OmniVid backend.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import Session
from ..src.database.connection import SessionLocal
from ..src.database.models import Video, User, Project
from ..src.database.repository import VideoRepository, ProjectRepository

# Test data
TEST_USER_ID = 1
TEST_PROJECT_ID = 1


def create_test_data(db: Session):
    """Create test user and project."""
    # Add test user if not exists
    user = db.query(User).filter(User.id == TEST_USER_ID).first()
    if not user:
        user = User(id=TEST_USER_ID, email="test@example.com", username="testuser")
        db.add(user)

    # Add test project if not exists
    project = db.query(Project).filter(Project.id == TEST_PROJECT_ID).first()
    if not project:
        project = Project(id=TEST_PROJECT_ID, name="Test Project", user_id=TEST_USER_ID)
        db.add(project)

    db.commit()
    return user, project


def test_concurrent_video_creations():
    """Test race condition when creating videos with the same name."""
    db = SessionLocal()
    create_test_data(db)
    db.close()

    video_title = "Race Condition Test Video"
    num_threads = 5

    def create_video():
        """Helper function to create a video."""
        db = SessionLocal()
        try:
            video_repo = VideoRepository(db)
            video = video_repo.create_video(
                {
                    "title": video_title,
                    "project_id": TEST_PROJECT_ID,
                    "user_id": TEST_USER_ID,
                }
            )
            db.commit()
            return video.id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    # Create videos in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(create_video) for _ in range(num_threads)]
        results = []

        for future in as_completed(futures):
            try:
                video_id = future.result()
                results.append(video_id)
            except Exception as e:
                # We expect some to fail due to unique constraint
                assert (
                    "duplicate key" in str(e).lower()
                    or "unique constraint" in str(e).lower()
                )

    # Verify only one video was created
    db = SessionLocal()
    videos = db.query(Video).filter(Video.title == video_title).all()
    db.close()

    assert len(videos) == 1, "Should only be one video with the same title"


def test_project_update_race_condition():
    """Test race condition when updating project settings."""
    db = SessionLocal()
    _, project = create_test_data(db)
    db.close()

    num_threads = 5
    initial_version = project.version

    def update_project(thread_num):
        """Helper function to update project."""
        db = SessionLocal()
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_project(TEST_PROJECT_ID)

            # Simulate some work
            time.sleep(0.1)

            # Update project with new settings
            project.settings = f"{{'thread_{thread_num}': 'updated'}}"
            project = project_repo.update_project(project.id, project)
            db.commit()
            return project.version
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    # Update project in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(update_project, i) for i in range(num_threads)]
        versions = []

        for future in as_completed(futures):
            try:
                version = future.result()
                versions.append(version)
            except Exception as e:
                # We expect some to fail due to version conflict
                assert "version" in str(e).lower()

    # Verify version was incremented correctly
    db = SessionLocal()
    project = db.query(Project).filter(Project.id == TEST_PROJECT_ID).first()
    db.close()

    # The final version should be initial + number of successful updates
    assert project.version > initial_version
    assert project.version <= initial_version + num_threads


def test_balance_update_race_condition():
    """Test race condition when updating user balance."""
    db = SessionLocal()
    user, _ = create_test_data(db)
    user.balance = 100  # Starting balance
    db.commit()
    db.close()

    num_threads = 10
    amount_per_thread = 10

    def update_balance():
        """Helper function to update user balance."""
        db = SessionLocal()
        try:
            # Use SELECT ... FOR UPDATE to lock the row
            user = (
                db.query(User).with_for_update().filter(User.id == TEST_USER_ID).first()
            )
            current_balance = user.balance

            # Simulate some work
            time.sleep(0.01)

            # Update balance
            user.balance = current_balance + amount_per_thread
            db.commit()
            return user.balance
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    # Update balance in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(update_balance) for _ in range(num_threads)]
        balances = []

        for future in as_completed(futures):
            try:
                balance = future.result()
                balances.append(balance)
            except Exception as e:
                pytest.fail(f"Unexpected error: {e}")

    # Verify final balance
    db = SessionLocal()
    user = db.query(User).filter(User.id == TEST_USER_ID).first()
    db.close()

    expected_balance = 100 + (num_threads * amount_per_thread)
    assert (
        user.balance == expected_balance
    ), f"Expected balance {expected_balance}, got {user.balance}"
