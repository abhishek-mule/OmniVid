from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.routers import videos, websocket
from app.database import async_engine
from app.models.video import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting OmniVid API...")
    
    # Create output directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    print(f"📁 Upload directory: {settings.UPLOAD_DIR}")
    print(f"📁 Output directory: {settings.OUTPUT_DIR}")
    print(f"🔗 Redis URL: {settings.REDIS_URL}")
    print(f"🗄️  Database: {settings.POSTGRES_DB}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down OmniVid API...")
    await async_engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Video Generation Platform with FastAPI, Celery, PostgreSQL, and Remotion",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router, prefix=settings.API_V1_PREFIX)
app.include_router(websocket.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OmniVid API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "celery": "running"
    }


@app.get(f"{settings.API_V1_PREFIX}/info")
async def api_info():
    """API information"""
    return {
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "endpoints": {
            "videos": f"{settings.API_V1_PREFIX}/videos",
            "websocket": f"{settings.API_V1_PREFIX}/ws/videos/{{video_id}}",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "REST API for video generation",
            "WebSocket for real-time progress",
            "Celery distributed task queue",
            "PostgreSQL database",
            "Multiple rendering engines (Remotion, FFmpeg, Manim, Blender)"
        ]
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
