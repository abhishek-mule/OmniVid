"""
Unit tests for the health check endpoints.
"""
from fastapi import status

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "OmniVid" in response.json()["message"]
