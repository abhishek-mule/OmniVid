import os
import time
import uuid
import json
import subprocess
from datetime import datetime
from celery import Task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.video import Video, VideoStatus
from app.config import settings
import redis

# Redis client for progress updates
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


class CallbackTask(Task):
    """Base task with progress callback"""
    
    def update_progress(self, video_id: str, progress: float, stage: str, status: VideoStatus):
        """Update video progress in database and broadcast via Redis"""
        db = SessionLocal()
        try:
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.progress = progress
                video.current_stage = stage
                video.status = status
                video.updated_at = datetime.utcnow()
                
                if status == VideoStatus.RENDERING and not video.started_at:
                    video.started_at = datetime.utcnow()
                
                db.commit()
                
                # Broadcast to WebSocket clients via Redis
                message = {
                    "video_id": video_id,
                    "progress": progress,
                    "stage": stage,
                    "status": status.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
                redis_client.publish(f"video:{video_id}", json.dumps(message))
                
        except Exception as e:
            print(f"Error updating progress: {e}")
            db.rollback()
        finally:
            db.close()


@celery_app.task(bind=True, base=CallbackTask)
def render_video(self, video_id: str, render_engine: str = "remotion"):
    """
    Main video rendering task
    Flow: PENDING → PARSING → RENDERING → ENCODING → FINALIZING → SUCCESS
    """
    db = SessionLocal()
    
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # Update task ID
        video.celery_task_id = self.request.id
        db.commit()
        
        # Stage 1: PARSING (0-25%)
        self.update_progress(video_id, 0, "Parsing", VideoStatus.PARSING)
        time.sleep(2)  # Simulate parsing
        parsed_data = parse_prompt(video.prompt)
        self.update_progress(video_id, 25, "Parsing", VideoStatus.PARSING)
        
        # Stage 2: RENDERING (25-50%)
        self.update_progress(video_id, 25, "Rendering", VideoStatus.RENDERING)
        
        if render_engine == "remotion":
            output_path = process_with_remotion(video, parsed_data, self, video_id)
        elif render_engine == "ffmpeg":
            output_path = process_with_ffmpeg(video, parsed_data, self, video_id)
        elif render_engine == "manim":
            output_path = process_with_manim(video, parsed_data, self, video_id)
        elif render_engine == "blender":
            output_path = process_with_blender(video, parsed_data, self, video_id)
        else:
            output_path = process_with_remotion(video, parsed_data, self, video_id)
        
        self.update_progress(video_id, 50, "Rendering", VideoStatus.RENDERING)
        
        # Stage 3: ENCODING (50-75%)
        self.update_progress(video_id, 50, "Encoding", VideoStatus.ENCODING)
        encoded_path = encode_video(output_path, video, self, video_id)
        self.update_progress(video_id, 75, "Encoding", VideoStatus.ENCODING)
        
        # Stage 4: FINALIZING (75-100%)
        self.update_progress(video_id, 75, "Finalizing", VideoStatus.FINALIZING)
        final_url = finalize_video(encoded_path, video, self, video_id)
        self.update_progress(video_id, 100, "Finalizing", VideoStatus.FINALIZING)
        
        # Mark as SUCCESS
        video.status = VideoStatus.SUCCESS
        video.progress = 100
        video.output_url = final_url
        video.output_path = encoded_path
        video.completed_at = datetime.utcnow()
        video.file_size = os.path.getsize(encoded_path) if os.path.exists(encoded_path) else 0
        db.commit()
        
        # Final broadcast
        message = {
            "video_id": video_id,
            "progress": 100,
            "stage": "Complete",
            "status": "success",
            "output_url": final_url,
            "timestamp": datetime.utcnow().isoformat()
        }
        redis_client.publish(f"video:{video_id}", json.dumps(message))
        
        return {
            "video_id": video_id,
            "status": "success",
            "output_url": final_url
        }
        
    except Exception as e:
        # Mark as FAILED
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            video.completed_at = datetime.utcnow()
            db.commit()
        
        # Broadcast failure
        message = {
            "video_id": video_id,
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        redis_client.publish(f"video:{video_id}", json.dumps(message))
        
        raise
    
    finally:
        db.close()


def parse_prompt(prompt: str) -> dict:
    """Parse the user prompt and extract video requirements"""
    # In production, this would use AI/NLP to parse the prompt
    # For now, return basic structure
    return {
        "prompt": prompt,
        "scenes": [{"description": prompt, "duration": 5}],
        "style": "cinematic",
        "transitions": ["fade"]
    }


def process_with_remotion(video: Video, parsed_data: dict, task, video_id: str) -> str:
    """Process video using Remotion (React-based video rendering)"""
    output_dir = os.path.join(settings.OUTPUT_DIR, video_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "remotion_output.mp4")
    
    # Simulate Remotion rendering with progress updates
    for i in range(26, 51, 5):
        time.sleep(1)
        task.update_progress(video_id, i, "Rendering", VideoStatus.RENDERING)
    
    # In production, you would call Remotion CLI:
    # subprocess.run([
    #     "npx", "remotion", "render",
    #     "src/index.tsx",
    #     "--props", json.dumps(parsed_data),
    #     "--output", output_path
    # ])
    
    # For demo, create a placeholder file
    with open(output_path, 'wb') as f:
        f.write(b'REMOTION_VIDEO_PLACEHOLDER')
    
    return output_path


def process_with_ffmpeg(video: Video, parsed_data: dict, task, video_id: str) -> str:
    """Process video using FFmpeg"""
    output_dir = os.path.join(settings.OUTPUT_DIR, video_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ffmpeg_output.mp4")
    
    # Simulate FFmpeg rendering
    for i in range(26, 51, 5):
        time.sleep(1)
        task.update_progress(video_id, i, "Rendering", VideoStatus.RENDERING)
    
    # In production, use FFmpeg commands:
    # subprocess.run([
    #     "ffmpeg", "-f", "lavfi", "-i", f"color=c=blue:s={video.resolution}:d={video.duration}",
    #     "-vf", f"drawtext=text='{video.prompt}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
    #     "-r", str(video.fps),
    #     output_path
    # ])
    
    with open(output_path, 'wb') as f:
        f.write(b'FFMPEG_VIDEO_PLACEHOLDER')
    
    return output_path


def process_with_manim(video: Video, parsed_data: dict, task, video_id: str) -> str:
    """Process video using Manim (Mathematical animations)"""
    output_dir = os.path.join(settings.OUTPUT_DIR, video_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "manim_output.mp4")
    
    for i in range(26, 51, 5):
        time.sleep(1)
        task.update_progress(video_id, i, "Rendering", VideoStatus.RENDERING)
    
    with open(output_path, 'wb') as f:
        f.write(b'MANIM_VIDEO_PLACEHOLDER')
    
    return output_path


def process_with_blender(video: Video, parsed_data: dict, task, video_id: str) -> str:
    """Process video using Blender (3D rendering)"""
    output_dir = os.path.join(settings.OUTPUT_DIR, video_id)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "blender_output.mp4")
    
    for i in range(26, 51, 5):
        time.sleep(1)
        task.update_progress(video_id, i, "Rendering", VideoStatus.RENDERING)
    
    with open(output_path, 'wb') as f:
        f.write(b'BLENDER_VIDEO_PLACEHOLDER')
    
    return output_path


def encode_video(input_path: str, video: Video, task, video_id: str) -> str:
    """Encode/compress the video"""
    output_path = input_path.replace("_output", "_encoded")
    
    # Simulate encoding with progress
    for i in range(51, 76, 5):
        time.sleep(0.8)
        task.update_progress(video_id, i, "Encoding", VideoStatus.ENCODING)
    
    # In production, use FFmpeg for encoding:
    # quality_map = {"fast": "ultrafast", "balanced": "medium", "best": "slow"}
    # preset = quality_map.get(video.quality, "medium")
    # subprocess.run([
    #     "ffmpeg", "-i", input_path,
    #     "-c:v", "libx264", "-preset", preset,
    #     "-crf", "23",
    #     output_path
    # ])
    
    # Copy placeholder for demo
    if os.path.exists(input_path):
        with open(input_path, 'rb') as src:
            with open(output_path, 'wb') as dst:
                dst.write(src.read())
    
    return output_path


def finalize_video(video_path: str, video: Video, task, video_id: str) -> str:
    """Finalize video and generate URL"""
    # Simulate finalization
    for i in range(76, 101, 5):
        time.sleep(0.5)
        task.update_progress(video_id, i, "Finalizing", VideoStatus.FINALIZING)
    
    # In production, upload to S3/CDN and return URL
    # For demo, return local path
    return f"/api/v1/videos/{video_id}/download"
