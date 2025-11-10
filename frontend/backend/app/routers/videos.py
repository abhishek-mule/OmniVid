from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import uuid
from datetime import datetime
import os

from app.database import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import VideoCreate, VideoResponse, VideoList
from app.tasks.video_tasks import render_video
from app.config import settings

router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/", response_model=VideoResponse, status_code=201)
async def create_video(
    video_data: VideoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new video generation request
    Flow: Parse request → Save to DB → Queue Celery task → Return video ID
    """
    # Generate unique ID
    video_id = str(uuid.uuid4())
    
    # Create video record
    video = Video(
        id=video_id,
        prompt=video_data.prompt,
        resolution=video_data.resolution,
        fps=video_data.fps,
        duration=video_data.duration,
        quality=video_data.quality,
        render_engine=video_data.render_engine,
        status=VideoStatus.PENDING,
        progress=0.0,
    )
    
    db.add(video)
    await db.commit()
    await db.refresh(video)
    
    # Queue Celery task (async)
    task = render_video.delay(
        video_id=video_id,
        render_engine=video_data.render_engine.value
    )
    
    # Update with task ID
    video.celery_task_id = task.id
    await db.commit()
    
    return video.to_dict()


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get video status and details"""
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return video.to_dict()


@router.get("/", response_model=VideoList)
async def list_videos(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all videos with pagination"""
    query = select(Video).order_by(desc(Video.created_at))
    
    if status:
        query = query.where(Video.status == status)
    
    # Get total count
    count_result = await db.execute(
        select(Video).where(Video.status == status) if status else select(Video)
    )
    total = len(count_result.scalars().all())
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    videos = result.scalars().all()
    
    return {
        "videos": [v.to_dict() for v in videos],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{video_id}/download")
async def download_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Download the generated video file"""
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status != VideoStatus.SUCCESS:
        raise HTTPException(
            status_code=400,
            detail=f"Video is not ready. Current status: {video.status.value}"
        )
    
    if not video.output_path or not os.path.exists(video.output_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video.output_path,
        media_type="video/mp4",
        filename=f"omnivid_{video_id}.mp4"
    )


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a video and its files"""
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Delete file if exists
    if video.output_path and os.path.exists(video.output_path):
        try:
            os.remove(video.output_path)
            # Also remove directory if empty
            output_dir = os.path.dirname(video.output_path)
            if os.path.exists(output_dir) and not os.listdir(output_dir):
                os.rmdir(output_dir)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # Delete from database
    await db.delete(video)
    await db.commit()
    
    return {"message": "Video deleted successfully", "video_id": video_id}


@router.post("/{video_id}/cancel")
async def cancel_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a video generation task"""
    result = await db.execute(
        select(Video).where(Video.id == video_id)
    )
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video.status in [VideoStatus.SUCCESS, VideoStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel completed or failed video"
        )
    
    # Revoke Celery task
    if video.celery_task_id:
        from app.celery_app import celery_app
        celery_app.control.revoke(video.celery_task_id, terminate=True)
    
    # Update status
    video.status = VideoStatus.FAILED
    video.error_message = "Cancelled by user"
    video.completed_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Video generation cancelled", "video_id": video_id}
