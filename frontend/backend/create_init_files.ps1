# PowerShell script to create __init__.py files for FastAPI backend
# Run this from the backend directory

Write-Host "Creating __init__.py files for FastAPI backend..." -ForegroundColor Green

# Create directories if they don't exist
$directories = @("app", "app\routers", "app\engines", "app\tasks", "app\models", "app\utils", "app\schemas")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Yellow
    }
}

# app/__init__.py (Root package with version info)
$appInit = @'
"""
OmniVid AI Backend Application

AI-powered video generation platform with FastAPI, Celery, PostgreSQL, and Remotion.
"""

__version__ = "1.0.0"
__author__ = "OmniVid Team"
__description__ = "Video generation API with distributed task processing"

from app.config import settings

__all__ = ["settings"]
'@

Set-Content -Path "app\__init__.py" -Value $appInit -Encoding UTF8
Write-Host "Created: app\__init__.py" -ForegroundColor Cyan

# app/routers/__init__.py (Router imports)
$routersInit = @'
"""
API Routers

REST API endpoints and WebSocket connections.
"""

from app.routers.videos import router as videos_router
from app.routers.websocket import router as websocket_router

__all__ = [
    "videos_router",
    "websocket_router",
]
'@

Set-Content -Path "app\routers\__init__.py" -Value $routersInit -Encoding UTF8
Write-Host "Created: app\routers\__init__.py" -ForegroundColor Cyan

# app/engines/__init__.py (Rendering engines - placeholder for future)
$enginesInit = @'
"""
Video Rendering Engines

Adapters for different video rendering engines:
- Remotion (React-based)
- FFmpeg (Command-line)
- Manim (Mathematical animations)
- Blender (3D rendering)
"""

# Placeholder for future engine implementations
# from app.engines.base_engine import BaseEngine
# from app.engines.remotion_adapter import RemotionAdapter
# from app.engines.ffmpeg_adapter import FFmpegAdapter

__all__ = []
'@

Set-Content -Path "app\engines\__init__.py" -Value $enginesInit -Encoding UTF8
Write-Host "Created: app\engines\__init__.py" -ForegroundColor Cyan

# app/tasks/__init__.py (Celery tasks)
$tasksInit = @'
"""
Celery Tasks

Distributed video rendering tasks with progress tracking.
"""

from app.tasks.video_tasks import render_video

__all__ = [
    "render_video",
]
'@

Set-Content -Path "app\tasks\__init__.py" -Value $tasksInit -Encoding UTF8
Write-Host "Created: app\tasks\__init__.py" -ForegroundColor Cyan

# app/models/__init__.py (Database models)
$modelsInit = @'
"""
Database Models

SQLAlchemy ORM models for PostgreSQL.
"""

from app.models.video import Video, VideoStatus, RenderEngine

__all__ = [
    "Video",
    "VideoStatus",
    "RenderEngine",
]
'@

Set-Content -Path "app\models\__init__.py" -Value $modelsInit -Encoding UTF8
Write-Host "Created: app\models\__init__.py" -ForegroundColor Cyan

# app/schemas/__init__.py (Pydantic schemas)
$schemasInit = @'
"""
Pydantic Schemas

Request/response models for API validation.
"""

from app.schemas.video import (
    VideoCreate,
    VideoResponse,
    VideoProgress,
    VideoList,
)

__all__ = [
    "VideoCreate",
    "VideoResponse",
    "VideoProgress",
    "VideoList",
]
'@

Set-Content -Path "app\schemas\__init__.py" -Value $schemasInit -Encoding UTF8
Write-Host "Created: app\schemas\__init__.py" -ForegroundColor Cyan

# app/utils/__init__.py (Utility functions)
$utilsInit = @'
"""
Utility Functions

Helper functions for video processing, file handling, and common operations.
"""

# Placeholder for utility functions
# from app.utils.file_handler import save_file, delete_file
# from app.utils.video_utils import get_video_metadata, create_thumbnail

__all__ = []
'@

Set-Content -Path "app\utils\__init__.py" -Value $utilsInit -Encoding UTF8
Write-Host "Created: app\utils\__init__.py" -ForegroundColor Cyan

Write-Host "`nAll __init__.py files created successfully!" -ForegroundColor Green
Write-Host "`nCreated files:" -ForegroundColor Yellow
Write-Host "  - app\__init__.py (version: 1.0.0)" -ForegroundColor White
Write-Host "  - app\routers\__init__.py" -ForegroundColor White
Write-Host "  - app\engines\__init__.py" -ForegroundColor White
Write-Host "  - app\tasks\__init__.py" -ForegroundColor White
Write-Host "  - app\models\__init__.py" -ForegroundColor White
Write-Host "  - app\schemas\__init__.py" -ForegroundColor White
Write-Host "  - app\utils\__init__.py" -ForegroundColor White

Write-Host "`nVerifying files..." -ForegroundColor Yellow
Get-ChildItem -Path "app" -Recurse -Filter "__init__.py" | ForEach-Object {
    Write-Host "  OK $($_.FullName)" -ForegroundColor Green
}

Write-Host "`nDone! Your FastAPI backend package structure is ready." -ForegroundColor Green
