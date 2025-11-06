from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.video import VideoStatus, RenderEngine


class VideoCreate(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500, description="Video description")
    resolution: str = Field(default="1080p", pattern="^(720p|1080p|2k|4k)$")
    fps: int = Field(default=30, ge=24, le=60)
    duration: int = Field(default=15, ge=5, le=60, description="Duration in seconds")
    quality: str = Field(default="balanced", pattern="^(fast|balanced|best)$")
    render_engine: Optional[RenderEngine] = RenderEngine.REMOTION


class VideoResponse(BaseModel):
    id: str
    user_id: Optional[str]
    prompt: str
    resolution: str
    fps: int
    duration: int
    quality: str
    render_engine: Optional[str]
    status: str
    progress: float
    current_stage: Optional[str]
    celery_task_id: Optional[str]
    output_url: Optional[str]
    file_size: Optional[int]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class VideoProgress(BaseModel):
    video_id: str
    progress: float
    stage: str
    status: str
    timestamp: datetime


class VideoList(BaseModel):
    videos: list[VideoResponse]
    total: int
    page: int
    page_size: int
