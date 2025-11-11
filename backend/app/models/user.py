from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
from typing import Optional
from pydantic import BaseModel, Field, validator
from ..utils.avatar import get_avatar_url

class UserBase(BaseModel):
    """Base user model for request/response schemas"""
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """User creation model"""
    password: str

class UserUpdate(UserBase):
    """User update model"""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """Base model for database operations"""
    id: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

    @validator('avatar_url', pre=True, always=True)
    def set_avatar_url(cls, v, values):
        """Generate avatar URL if not provided"""
        if v is None and 'id' in values:
            return get_avatar_url(values['id'])
        return v

class User(UserInDBBase):
    """User model for response"""
    pass

class UserInDB(UserInDBBase):
    """User model for database operations"""
    hashed_password: str

# SQLAlchemy model
class DBUser(Base):
    """Database model for users"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def avatar(self) -> str:
        """Get the user's avatar URL, generating one if not set"""
        if self.avatar_url:
            return self.avatar_url
        return get_avatar_url(self.id)
