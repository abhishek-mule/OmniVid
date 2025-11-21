"""
Database integration tests for OmniVid backend.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..src.database.connection import Base, get_db
from ..src.database.models import User, Project, Video, Asset, Job
from ..src.database.repository import (
    UserRepository,
    ProjectRepository,
    VideoRepository,
    AssetRepository,
    JobRepository,
)
from ..src.database.schemas import (
    UserCreate,
    ProjectCreate,
    VideoCreate,
    AssetCreate,
    JobCreate,
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user_repository(db):
    return UserRepository(db)


@pytest.fixture
def project_repository(db):
    return ProjectRepository(db)


@pytest.fixture
def video_repository(db):
    return VideoRepository(db)


@pytest.fixture
def asset_repository(db):
    return AssetRepository(db)


@pytest.fixture
def job_repository(db):
    return JobRepository(db)


# User tests
def test_create_user(user_repository):
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User",
    )

    user = user_repository.create_user(user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False


def test_get_user_by_email(user_repository):
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )

    created_user = user_repository.create_user(user_data)
    retrieved_user = user_repository.get_user_by_email("test@example.com")

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


def test_get_user_by_username(user_repository):
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )

    created_user = user_repository.create_user(user_data)
    retrieved_user = user_repository.get_user_by_username("testuser")

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == created_user.username


# Project tests
def test_create_project(project_repository, user_repository):
    # First create a user
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    # Then create a project
    project_data = ProjectCreate(
        title="Test Project", description="A test project", is_public=True
    )

    project = project_repository.create_project(user.id, project_data)

    assert project.id is not None
    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert project.user_id == user.id
    assert project.is_public is True
    assert project.status == "draft"


def test_get_projects_by_user(project_repository, user_repository):
    # Create user and projects
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    project_data1 = ProjectCreate(title="Project 1", is_public=True)
    project_data2 = ProjectCreate(title="Project 2", is_public=False)

    project_repository.create_project(user.id, project_data1)
    project_repository.create_project(user.id, project_data2)

    projects = project_repository.get_projects_by_user(user.id)

    assert len(projects) == 2
    assert projects[0].title == "Project 1"
    assert projects[1].title == "Project 2"


# Video tests
def test_create_video(video_repository, user_repository, project_repository):
    # Create user and project
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    project_data = ProjectCreate(title="Test Project", is_public=True)
    project = project_repository.create_project(user.id, project_data)

    # Create video
    video_data = VideoCreate(
        title="Test Video",
        prompt="Create a test video",
        project_id=project.id,
        settings='{"duration": 30}',
    )

    video = video_repository.create_video(video_data)

    assert video.id is not None
    assert video.title == "Test Video"
    assert video.prompt == "Create a test video"
    assert video.project_id == project.id
    assert video.status == "pending"
    assert video.progress == 0


def test_update_video_progress(video_repository, user_repository, project_repository):
    # Create user, project, and video
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    project_data = ProjectCreate(title="Test Project", is_public=True)
    project = project_repository.create_project(user.id, project_data)

    video_data = VideoCreate(
        title="Test Video", prompt="Create a test video", project_id=project.id
    )
    video = video_repository.create_video(video_data)

    # Update progress
    updated_video = video_repository.update_video_progress(video.id, 50, "processing")

    assert updated_video.progress == 50
    assert updated_video.status == "processing"

    # Update to completed
    completed_video = video_repository.update_video_progress(video.id, 100, "completed")

    assert completed_video.progress == 100
    assert completed_video.status == "completed"
    assert completed_video.completed_at is not None


# Job tests
def test_create_job(
    job_repository, user_repository, project_repository, video_repository
):
    # Create user, project, and video
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    project_data = ProjectCreate(title="Test Project", is_public=True)
    project = project_repository.create_project(user.id, project_data)

    video_data = VideoCreate(
        title="Test Video", prompt="Create a test video", project_id=project.id
    )
    video = video_repository.create_video(video_data)

    # Create job
    job_data = JobCreate(task_id="test-task-id-123", video_id=video.id)

    job = job_repository.create_job(job_data)

    assert job.id is not None
    assert job.task_id == "test-task-id-123"
    assert job.video_id == video.id
    assert job.status == "pending"
    assert job.progress == 0


def test_get_job_by_task_id(
    job_repository, user_repository, project_repository, video_repository
):
    # Create user, project, video, and job
    user_data = UserCreate(
        email="test@example.com", username="testuser", password="testpassword"
    )
    user = user_repository.create_user(user_data)

    project_data = ProjectCreate(title="Test Project", is_public=True)
    project = project_repository.create_project(user.id, project_data)

    video_data = VideoCreate(
        title="Test Video", prompt="Create a test video", project_id=project.id
    )
    video = video_repository.create_video(video_data)

    job_data = JobCreate(task_id="test-task-id-123", video_id=video.id)

    created_job = job_repository.create_job(job_data)
    retrieved_job = job_repository.get_job_by_task_id("test-task-id-123")

    assert retrieved_job is not None
    assert retrieved_job.id == created_job.id
    assert retrieved_job.task_id == "test-task-id-123"
