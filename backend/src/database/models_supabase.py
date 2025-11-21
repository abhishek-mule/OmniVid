"""
Database models for Supabase integration
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String(255), primary_key=True)  # UUID from Supabase
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(255), ForeignKey("user_profiles.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    status = Column(String(50), default="draft")  # draft, active, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("UserProfile", back_populates="projects")
    videos = relationship("Video", back_populates="project")
    assets = relationship("Asset", back_populates="project")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    duration = Column(Float, nullable=True)  # in seconds
    status = Column(
        String(50), default="pending"
    )  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    settings = Column(Text, nullable=True)  # JSON string for video generation settings
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="videos")
    assets = relationship("Asset", back_populates="video")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    is_processed = Column(Boolean, default=False)
    asset_metadata = Column(
        "metadata", Text, nullable=True
    )  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="assets")
    video = relationship("Video", back_populates="assets")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, nullable=False)  # Celery task ID
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, started, success, failure
    progress = Column(Integer, default=0)  # 0-100
    result = Column(Text, nullable=True)  # JSON string for task result
    error = Column(Text, nullable=True)  # Error message if task failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
