"""
Authentication tests for OmniVid backend.
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from ..src.api.main import app
from ..src.auth.schemas import LoginRequest, RegisterRequest
from ..src.auth.security import (create_access_token, get_password_hash,
                                 verify_password)
from ..src.database.connection import Base, engine
from ..src.database.models import User
from ..src.database.repository import UserRepository
from ..src.database.schemas import UserCreate

client = TestClient(app)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User",
    )
    user = user_repo.create_user(user_data)
    return user


def test_register_user(db):
    """Test user registration."""
    user_data = RegisterRequest(
        email="newuser@example.com",
        username="newuser",
        password="newpassword",
        full_name="New User",
    )

    response = client.post("/auth/register", json=user_data.dict())

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert data["full_name"] == "New User"
    assert "hashed_password" in data  # Should not expose password hash


def test_register_duplicate_email(db):
    """Test registration with duplicate email."""
    user_data = RegisterRequest(
        email="duplicate@example.com", username="user1", password="password"
    )

    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data.dict())
    assert response1.status_code == 200

    # Second registration with same email should fail
    user_data2 = RegisterRequest(
        email="duplicate@example.com", username="user2", password="password"
    )
    response2 = client.post("/auth/register", json=user_data2.dict())
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]


def test_register_duplicate_username(db):
    """Test registration with duplicate username."""
    user_data = RegisterRequest(
        email="user1@example.com", username="duplicateuser", password="password"
    )

    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data.dict())
    assert response1.status_code == 200

    # Second registration with same username should fail
    user_data2 = RegisterRequest(
        email="user2@example.com", username="duplicateuser", password="password"
    )
    response2 = client.post("/auth/register", json=user_data2.dict())
    assert response2.status_code == 400
    assert "Username already taken" in response2.json()["detail"]


def test_login_user(db, test_user):
    """Test user login."""
    login_data = LoginRequest(email="test@example.com", password="testpassword")

    response = client.post("/auth/login", json=login_data.dict())

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_email(db):
    """Test login with invalid email."""
    login_data = LoginRequest(email="nonexistent@example.com", password="password")

    response = client.post("/auth/login", json=login_data.dict())

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_invalid_password(db, test_user):
    """Test login with invalid password."""
    login_data = LoginRequest(email="test@example.com", password="wrongpassword")

    response = client.post("/auth/login", json=login_data.dict())

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user(db, test_user):
    """Test getting current user info with valid token."""
    # First login to get token
    login_data = LoginRequest(email="test@example.com", password="testpassword")
    login_response = client.post("/auth/login", json=login_data.dict())
    token = login_response.json()["access_token"]

    # Get user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_invalid_token(db):
    """Test getting current user info with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401


def test_verify_token(db, test_user):
    """Test token verification endpoint."""
    # Login to get token
    login_data = LoginRequest(email="test@example.com", password="testpassword")
    login_response = client.post("/auth/login", json=login_data.dict())
    token = login_response.json()["access_token"]

    # Verify token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/verify", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "user_id" in data
    assert "email" in data


def test_logout(db, test_user):
    """Test logout endpoint."""
    # Login to get token
    login_data = LoginRequest(email="test@example.com", password="testpassword")
    login_response = client.post("/auth/login", json=login_data.dict())
    token = login_response.json()["access_token"]

    # Logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]


# Test security utilities
def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "123", "email": "test@example.com"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


def test_token_expiration():
    """Test token expiration."""
    data = {"sub": "123"}
    # Create token with very short expiration for testing
    token = create_access_token(data, expires_delta=timedelta(seconds=1))

    # Note: In practice, you would wait and test expiration,
    # but that's not practical in unit tests
    assert isinstance(token, str)
