from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.models import User, Project, Video, Asset, Job
from ..database.schemas import (
    UserCreate, UserUpdate,
    ProjectCreate, ProjectUpdate,
    VideoCreate, VideoUpdate,
    AssetCreate,
    JobCreate, JobUpdate
)

# User Repository
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create_user(self, user: UserCreate) -> User:
        hashed_password = UserRepository.get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user: UserUpdate) -> Optional[User]:
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: int) -> bool:
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        from ..auth.security import get_password_hash as secure_hash
        return secure_hash(password)

# Project Repository
class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_project(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_projects_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_public_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        return self.db.query(Project).filter(Project.is_public == True).offset(skip).limit(limit).all()
    
    def create_project(self, user_id: int, project: ProjectCreate) -> Project:
        db_project = Project(user_id=user_id, **project.dict())
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def update_project(self, project_id: int, project: ProjectUpdate) -> Optional[Project]:
        db_project = self.get_project(project_id)
        if db_project:
            update_data = project.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)
            self.db.commit()
            self.db.refresh(db_project)
        return db_project
    
    def delete_project(self, project_id: int) -> bool:
        db_project = self.get_project(project_id)
        if db_project:
            self.db.delete(db_project)
            self.db.commit()
            return True
        return False

# Video Repository
class VideoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_video(self, video_id: int) -> Optional[Video]:
        return self.db.query(Video).filter(Video.id == video_id).first()
    
    def get_videos_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Video]:
        return self.db.query(Video).filter(Video.project_id == project_id).offset(skip).limit(limit).all()
    
    def get_videos_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Video]:
        return self.db.query(Video).join(Project).filter(Project.user_id == user_id).offset(skip).limit(limit).all()
    
    def create_video(self, video: VideoCreate) -> Video:
        db_video = Video(**video.dict())
        self.db.add(db_video)
        self.db.commit()
        self.db.refresh(db_video)
        return db_video
    
    def update_video(self, video_id: int, video: VideoUpdate) -> Optional[Video]:
        db_video = self.get_video(video_id)
        if db_video:
            update_data = video.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_video, field, value)
            self.db.commit()
            self.db.refresh(db_video)
        return db_video
    
    def update_video_progress(self, video_id: int, progress: int, status: str = None) -> Optional[Video]:
        db_video = self.get_video(video_id)
        if db_video:
            db_video.progress = progress
            if status:
                db_video.status = status
            if status == "completed":
                from sqlalchemy.sql import func
                db_video.completed_at = func.now()
            self.db.commit()
            self.db.refresh(db_video)
        return db_video
    
    def delete_video(self, video_id: int) -> bool:
        db_video = self.get_video(video_id)
        if db_video:
            self.db.delete(db_video)
            self.db.commit()
            return True
        return False

# Asset Repository
class AssetRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_asset(self, asset_id: int) -> Optional[Asset]:
        return self.db.query(Asset).filter(Asset.id == asset_id).first()
    
    def get_assets_by_project(self, project_id: int) -> List[Asset]:
        return self.db.query(Asset).filter(Asset.project_id == project_id).all()
    
    def get_assets_by_video(self, video_id: int) -> List[Asset]:
        return self.db.query(Asset).filter(Asset.video_id == video_id).all()
    
    def create_asset(self, asset: AssetCreate, file_path: str, file_size: int) -> Asset:
        db_asset = Asset(
            project_id=asset.project_id,
            video_id=asset.video_id,
            filename=asset.filename,
            original_filename=asset.original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=asset.file_type,
            mime_type=asset.mime_type
        )
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)
        return db_asset
    
    def update_asset_processing_status(self, asset_id: int, is_processed: bool, asset_metadata: str = None) -> Optional[Asset]:
        db_asset = self.get_asset(asset_id)
        if db_asset:
            db_asset.is_processed = is_processed
            if asset_metadata:
                db_asset.asset_metadata = asset_metadata
            self.db.commit()
            self.db.refresh(db_asset)
        return db_asset

# Job Repository
class JobRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_job(self, job_id: int) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_job_by_task_id(self, task_id: str) -> Optional[Job]:
        return self.db.query(Job).filter(Job.task_id == task_id).first()
    
    def get_jobs_by_video(self, video_id: int) -> List[Job]:
        return self.db.query(Job).filter(Job.video_id == video_id).all()
    
    def create_job(self, job: JobCreate) -> Job:
        db_job = Job(**job.dict())
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job
    
    def update_job(self, job_id: int, job_update: JobUpdate) -> Optional[Job]:
        db_job = self.get_job(job_id)
        if db_job:
            update_data = job_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_job, field, value)
            if job_update.status in ["success", "failure"]:
                from sqlalchemy.sql import func
                db_job.completed_at = func.now()
            self.db.commit()
            self.db.refresh(db_job)
        return db_job