from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.auth.security import get_current_user
from src.database.connection import get_db
from src.database.repository import ProjectRepository, VideoRepository
from src.database.schemas import Video, VideoCreate, VideoUpdate

router = APIRouter()


@router.post("/videos", response_model=Video)
def create_video(
    video: VideoCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new video generation request."""
    # Verify that the project exists and user has permission
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create videos in this project",
        )

    # Create the video
    video_repo = VideoRepository(db)
    created_video = video_repo.create_video(video)
    return created_video


@router.get("/videos", response_model=List[Video])
def get_videos(
    project_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get videos for the current user."""
    video_repo = VideoRepository(db)

    if project_id:
        # Get videos for specific project
        project_repo = ProjectRepository(db)
        project = project_repo.get_project(project_id)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        if project.user_id != current_user["user_id"] and not project.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this project's videos",
            )

        videos = video_repo.get_videos_by_project(project_id, skip, limit)
    else:
        # Get all videos for the user
        videos = video_repo.get_videos_by_user(current_user["user_id"], skip, limit)

    return videos


@router.get("/videos/{video_id}", response_model=Video)
def get_video(
    video_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific video."""
    video_repo = VideoRepository(db)
    video = video_repo.get_video(video_id)

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project.user_id != current_user["user_id"] and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this video",
        )

    return video


@router.put("/videos/{video_id}", response_model=Video)
def update_video(
    video_id: int,
    video_update: VideoUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a video."""
    video_repo = VideoRepository(db)
    video = video_repo.get_video(video_id)

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this video",
        )

    # Don't allow updates to videos that are already completed
    if video.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed video",
        )

    updated_video = video_repo.update_video(video_id, video_update)
    return updated_video


@router.delete("/videos/{video_id}")
def delete_video(
    video_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a video."""
    video_repo = VideoRepository(db)
    video = video_repo.get_video(video_id)

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this video",
        )

    # Don't allow deletion of videos that are processing
    if video.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete video that is currently processing",
        )

    success = video_repo.delete_video(video_id)
    if success:
        return {"message": "Video deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video",
        )


@router.get("/videos/{video_id}/status", response_model=dict)
def get_video_status(
    video_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the status and progress of a video."""
    video_repo = VideoRepository(db)
    video = video_repo.get_video(video_id)

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project.user_id != current_user["user_id"] and not project.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this video status",
        )

    return {
        "video_id": video.id,
        "status": video.status,
        "progress": video.progress,
        "created_at": video.created_at,
        "updated_at": video.updated_at,
        "completed_at": video.completed_at,
        "error_message": video.error_message,
    }


@router.post("/videos/{video_id}/retry")
def retry_video_generation(
    video_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retry video generation for a failed video."""
    video_repo = VideoRepository(db)
    video = video_repo.get_video(video_id)

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video not found"
        )

    # Check permissions
    project_repo = ProjectRepository(db)
    project = project_repo.get_project(video.project_id)

    if project.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to retry this video",
        )

    # Only allow retry for failed videos
    if video.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed videos",
        )

    # Reset video to pending status
    updated_video = video_repo.update_video_progress(video_id, 0, "pending")
    updated_video.error_message = None

    return {"message": "Video generation retry queued", "video_id": video_id}
