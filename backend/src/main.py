from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="OmniVid API",
    description="Backend API for OmniVid video platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data model
class Video(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None

# In-memory storage (replace with database later)
videos_db = []

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to OmniVid API"}

# Get all videos
@app.get("/videos", response_model=List[Video])
async def get_videos():
    return videos_db

# Get video by ID
@app.get("/videos/{video_id}", response_model=Video)
async def get_video(video_id: str):
    for video in videos_db:
        if video["id"] == video_id:
            return video
    raise HTTPException(status_code=404, detail="Video not found")

# Create a new video
@app.post("/videos", response_model=Video, status_code=status.HTTP_201_CREATED)
async def create_video(video: Video):
    videos_db.append(video.dict())
    return video

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
