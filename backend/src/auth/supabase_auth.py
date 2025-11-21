"""
Supabase authentication middleware and utilities for FastAPI backend
"""

import logging
import os
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

logger = logging.getLogger(__name__)


# Create Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client with service role key for server-side operations."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase environment variables")

    return create_client(supabase_url, supabase_key)


# Security scheme
security = HTTPBearer()


class SupabaseAuth:
    def __init__(self):
        self.client = get_supabase_client()

    def get_current_user(self, request: Request) -> Dict[str, Any]:
        """Extract and validate user from Supabase session token."""
        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1]

        try:
            # Verify the token with Supabase
            response = self.client.auth.get_user(token)

            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = response.user
            return {
                "id": user.id,
                "email": user.email,
                "raw_user_meta_data": user.user_metadata,
                "is_active": True,  # Supabase users are considered active by default
            }

        except Exception as e:
            logger.error(f"Error validating Supabase token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def create_user_profile(
        self, user_id: str, email: str, user_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create or update user profile in the database."""
        try:
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": user_metadata.get("full_name", ""),
                "username": user_metadata.get("username", email.split("@")[0]),
                "is_active": True,
                "is_superuser": False,
            }

            # Upsert user profile
            response = self.client.table("user_profiles").upsert(profile_data).execute()

            if response.data:
                return response.data[0]
            else:
                logger.error("Failed to create user profile")
                return profile_data

        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user profile",
            )

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from the database."""
        try:
            response = (
                self.client.table("user_profiles")
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None


# Global instance
supabase_auth = SupabaseAuth()


# Dependency to get current authenticated user
def get_current_supabase_user(request: Request):
    """Dependency to get current authenticated Supabase user."""
    return supabase_auth.get_current_user(request)


# Optional dependency for backwards compatibility
def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Optional dependency - returns None if no valid token provided."""
    try:
        return supabase_auth.get_current_user(request)
    except HTTPException:
        return None


# User creation helper
def create_user_from_supabase(auth_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a user entry from Supabase auth data."""
    user_id = auth_data["id"]
    email = auth_data["email"]
    metadata = auth_data.get("raw_user_meta_data", {})

    # Try to get existing profile
    existing_profile = supabase_auth.get_user_profile(user_id)

    if not existing_profile:
        # Create new profile
        profile = supabase_auth.create_user_profile(user_id, email, metadata)
    else:
        # Update existing profile with latest metadata
        supabase_auth.create_user_profile(user_id, email, metadata)
        profile = existing_profile

    return profile
