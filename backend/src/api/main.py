from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database
from ..database.connection import get_db, engine
from ..database.models import Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniVid API",
    description="Backend API for OmniVid application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to OmniVid API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import routers here
from .routes.health import router as health_router
from .routes.projects import router as projects_router
from .routes.videos import router as videos_router
from .routes.files import router as files_router
from .routes.websocket import router as websocket_router
from ..auth.routes import router as auth_router

app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(videos_router, prefix="/api", tags=["videos"])
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(websocket_router, prefix="", tags=["websocket"])
app.include_router(health_router)
