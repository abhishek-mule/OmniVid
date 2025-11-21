from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    status: Optional[str] = None


class Project(ProjectBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: User
    videos: List["Video"] = []

    class Config:
        from_attributes = True


# Video Schemas
class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    prompt: str


class VideoCreate(VideoBase):
    project_id: int
    settings: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    settings: Optional[str] = None


class Video(VideoBase):
    id: int
    project_id: int
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[float] = None
    status: str
    progress: int
    settings: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project: Project

    class Config:
        from_attributes = True


# Asset Schemas
class AssetBase(BaseModel):
    filename: str
    original_filename: str
    file_type: str
    mime_type: str


class AssetCreate(AssetBase):
    project_id: Optional[int] = None
    video_id: Optional[int] = None


class Asset(AssetBase):
    id: int
    file_path: str
    file_size: int
    project_id: Optional[int] = None
    video_id: Optional[int] = None
    is_processed: bool
    asset_metadata: Optional[str] = None
    created_at: datetime
    project: Optional[Project] = None
    video: Optional[Video] = None

    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    task_id: str
    video_id: int


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None


class Job(JobBase):
    id: int
    status: str
    progress: int
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Update forward references
Project.model_rebuild()
Video.model_rebuild()
Asset.model_rebuild()
