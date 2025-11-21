"""
Updated authentication routes with Supabase integration
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..auth.supabase_auth import create_user_from_supabase, get_current_supabase_user
from ..database.connection import get_db
from ..database.models_supabase import UserProfile
from ..database.repository import UserRepository
from ..database.schemas import User, UserCreate

router = APIRouter()


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None


@router.post("/profile")
def create_user_profile(
    current_user: dict = Depends(get_current_supabase_user),
    db: Session = Depends(get_db),
):
    """Create or update user profile from Supabase auth data."""
    try:
        # Create user from Supabase data
        user_data = create_user_from_supabase(current_user)

        # Add to database
        profile = UserProfile(
            id=current_user["id"],
            email=current_user["email"],
            username=user_data["username"],
            full_name=user_data.get("full_name"),
            is_active=True,
            is_superuser=False,
        )

        db.merge(profile)
        db.commit()

        return {
            "message": "Profile created successfully",
            "profile": {
                "id": profile.id,
                "email": profile.email,
                "username": profile.username,
                "full_name": profile.full_name,
                "is_active": profile.is_active,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}",
        )


@router.get("/profile", response_model=ProfileResponse)
def get_user_profile(
    current_user: dict = Depends(get_current_supabase_user),
    db: Session = Depends(get_db),
):
    """Get current user profile."""
    profile = db.query(UserProfile).filter(UserProfile.id == current_user["id"]).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return ProfileResponse(
        id=profile.id,
        email=profile.email,
        username=profile.username,
        full_name=profile.full_name,
        is_active=profile.is_active,
        created_at=profile.created_at.isoformat() if profile.created_at else None,
    )


@router.put("/profile", response_model=ProfileResponse)
def update_user_profile(
    profile_data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_supabase_user),
    db: Session = Depends(get_db),
):
    """Update user profile."""
    profile = db.query(UserProfile).filter(UserProfile.id == current_user["id"]).first()

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Update fields if provided
    if profile_data.username:
        profile.username = profile_data.username
    if profile_data.full_name is not None:
        profile.full_name = profile_data.full_name

    profile.updated_at = func.now()
    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        email=profile.email,
        username=profile.username,
        full_name=profile.full_name,
        is_active=profile.is_active,
        created_at=profile.created_at.isoformat() if profile.created_at else None,
    )


@router.post("/logout")
def logout_user():
    """Logout user - handled client-side by clearing Supabase session."""
    return {"message": "Successfully logged out"}


@router.get("/verify")
def verify_token(current_user: dict = Depends(get_current_supabase_user)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user_id": current_user["id"],
        "email": current_user["email"],
    }


@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_supabase_user)):
    """Get current user information (alias for /verify)."""
    return current_user
