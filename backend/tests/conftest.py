"""
Pytest configuration and fixtures for testing the OmniVid backend.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def test_assets_dir() -> Path:
    """Return the path to the test assets directory."""
    return Path(__file__).parent / "test_assets"


# Create test assets directory if it doesn't exist
os.makedirs(Path(__file__).parent / "test_assets", exist_ok=True)
