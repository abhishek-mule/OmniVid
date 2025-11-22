import asyncio
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

# Import database and models
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database.connection import Base, create_tables, engine

# Routes imports come later based on USE_SUPABASE setting


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import routers here to avoid import issues
    # Import auth routes conditionally based on USE_SUPABASE
    import os

    from .routes.files import router as files_router
    from .routes.health import router as health_router
    from .routes.projects import router as projects_router
    from .routes.videos import router as videos_router
    from .routes.websocket import router as websocket_router

    use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"

    if use_supabase:
        from src.auth.supabase_routes import router as auth_router

        # Initialize Supabase client - tables are managed by Supabase
        from src.core.supabase import get_supabase

        _ = get_supabase()  # Initialize the client
    else:
        from src.auth.routes import router as auth_router

        # Create database tables on startup when not using Supabase
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield  # App is running

    # Clean up on shutdown
    if not use_supabase:
        await engine.dispose()


app = FastAPI(
    title="OmniVid API",
    description="Backend API for OmniVid application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to OmniVid API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Import auth routes conditionally based on USE_SUPABASE
import os

from .routes.files import router as files_router

# Import routers here
from .routes.health import router as health_router
from .routes.projects import router as projects_router
from .routes.videos import router as videos_router
from .routes.websocket import router as websocket_router

use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"

if use_supabase:
    from src.auth.supabase_routes import router as auth_router
else:
    from src.auth.routes import router as auth_router

app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(videos_router, prefix="/api", tags=["videos"])
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(websocket_router, prefix="", tags=["websocket"])
app.include_router(health_router)

# AI routes
from .routes.ai import router as ai_router

app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
