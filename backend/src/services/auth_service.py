import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Conditionally import Supabase
use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"
if use_supabase:
    try:
        from src.core.supabase import get_supabase
    except ImportError:
        get_supabase = None
else:
    get_supabase = None

# JWT Configuration
SECRET_KEY = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user from the JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if use_supabase and get_supabase:
        # Get user from Supabase
        supabase = get_supabase()
        response = (
            supabase.table("users").select("*").eq("id", user_id).single().execute()
        )

        if not response.data:
            raise credentials_exception

        return response.data
    else:
        # Return basic user info from token (for non-Supabase mode)
        return {"id": user_id, "email": payload.get("email"), "is_active": True}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    # This is a placeholder. In a real app, use a proper password hashing library
    # like passlib with bcrypt
    return plain_password == hashed_password  # Insecure! Replace with proper hashing


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    # This is a placeholder. In a real app, use a proper password hashing library
    # like passlib with bcrypt
    return password  # Insecure! Replace with proper hashing
