from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any

from src.services.auth_service import (
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.core.supabase import get_supabase
from src.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict[str, Any]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    supabase = get_supabase()
    
    # Get user by email
    response = supabase.table("users").select("*").eq("email", form_data.username).single().execute()
    
    if not response.data or not verify_password(form_data.password, response.data.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(response.data["id"])},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": response.data["id"],
            "email": response.data["email"],
            "username": response.data.get("username"),
            "is_active": response.data.get("is_active", True)
        }
    }

@router.post("/register")
async def register_user(
    email: str,
    password: str,
    username: str,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """
    Register a new user
    """
    supabase = get_supabase()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("id").eq("email", email).execute()
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user in Supabase
    user_data = {
        "email": email,
        "hashed_password": get_password_hash(password),
        "username": username,
        "is_active": True,
        "is_superuser": False
    }
    
    try:
        new_user = supabase.table("users").insert(user_data).execute()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.data[0]["id"])},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.data[0]["id"],
                "email": email,
                "username": username,
                "is_active": True
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)) -> dict[str, Any]:
    """
    Get current user information
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user.get("username"),
        "is_active": current_user.get("is_active", True),
        "is_superuser": current_user.get("is_superuser", False)
    }
