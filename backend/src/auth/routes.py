from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..auth.schemas import LoginRequest, RegisterRequest, Token
from ..auth.security import (
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    verify_password,
)
from ..config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database.connection import get_db
from ..database.repository import UserRepository
from ..database.schemas import User, UserCreate

router = APIRouter()


@router.post("/register", response_model=User)
def register_user(user: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    user_repo = UserRepository(db)

    # Check if user already exists
    existing_user = user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    existing_username = user_repo.get_user_by_username(user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create new user
    db_user = UserCreate(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        password=user.password,
    )

    created_user = user_repo.create_user(db_user)
    return created_user


@router.post("/login", response_model=Token)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user_repo = UserRepository(db)

    # Get user by email
    user = user_repo.get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: dict = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user information."""
    user_repo = UserRepository(db)
    user = user_repo.get_user(current_user["user_id"])

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.post("/logout")
def logout_user(current_user: dict = Depends(get_current_active_user)):
    """Logout user (client-side token removal)."""
    # In a JWT-based system, logout is typically handled client-side
    # by removing the token. Server-side logout would require token blacklisting.
    return {"message": "Successfully logged out"}


@router.get("/verify")
def verify_token(current_user: dict = Depends(get_current_active_user)):
    """Verify if the current token is valid."""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user["email"],
    }
