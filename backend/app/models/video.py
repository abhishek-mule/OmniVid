from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    RENDERING = "rendering"
    ENCODING = "encoding"
    FINALIZING = "finalizing"
    SUCCESS = "success"
    FAILED = "failed"


class RenderEngine(str, enum.Enum):
    REMOTION = "remotion"
    FFMPEG = "ffmpeg"
    MANIM = "manim"
    BLENDER = "blender"


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # For future auth
    
    # Prompt and settings
    prompt = Column(Text, nullable=False)
    resolution = Column(String, default="1080p")
    fps = Column(Integer, default=30)
    duration = Column(Integer, default=15)  # in seconds
    quality = Column(String, default="balanced")
    
    # Rendering
    render_engine = Column(Enum(RenderEngine), default=RenderEngine.REMOTION)
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING, index=True)
    progress = Column(Float, default=0.0)  # 0-100
    current_stage = Column(String, nullable=True)
    
    # Task tracking
    celery_task_id = Column(String, unique=True, index=True, nullable=True)
    
    # Output
    output_url = Column(String, nullable=True)
    output_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    thumbnail_url = Column(String, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prompt": self.prompt,
            "resolution": self.resolution,
            "fps": self.fps,
            "duration": self.duration,
            "quality": self.quality,
            "render_engine": self.render_engine.value if self.render_engine else None,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "celery_task_id": self.celery_task_id,
            "output_url": self.output_url,
            "file_size": self.file_size,
            "thumbnail_url": self.thumbnail_url,
            "metadata": self.metadata,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
