from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.auth.security import get_current_user
from src.database.connection import get_db
from src.database.repository import ProjectRepository, VideoRepository
from src.database.schemas import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    Video,
    VideoCreate,
    VideoUpdate,
)

router = APIRouter()


@router.post("/projects", response_model=Project)
def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new project."""
    project_repo = ProjectRepository(db)
    created_project = project_repo.create_project(current_user["user_id"], project)
    return created_project


@router.get("/projects", response_model=List[Project])
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's projects."""
    project_repo = ProjectRepository(db)
    projects = project_repo.get_projects_by_user(current_user["user_id"], skip, limit)
    return projects


@router.get("/projects/{project_id}", response_model=Project)
def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific project."""
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Check if user owns the project or it's public
    if project.user_id != current_user["user_id"] and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project",
        )

    return project


@router.put("/projects/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a project."""
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this project",
        )

    updated_project = project_repo.update_project(project_id, project_update)
    return updated_project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project."""
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this project",
        )

    success = project_repo.delete_project(project_id)
    if success:
        return {"message": "Project deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project",
        )


@router.get("/projects/{project_id}/videos", response_model=List[Video])
def get_project_videos(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get videos for a project."""
    project_repo = ProjectRepository(db)
    video_repo = VideoRepository(db)

    project = project_repo.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Check permissions
    if project.user_id != current_user["user_id"] and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project's videos",
        )

    videos = video_repo.get_videos_by_project(project_id, skip, limit)
    return videos
