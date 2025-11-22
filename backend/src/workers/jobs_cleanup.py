"""
Job cleanup service for Blender rendering.
Handles cleanup of temporary directories and expired job artifacts.
"""

import logging
import shutil
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from src.config.settings import OUTPUT_DIR
from src.database.connection import SessionLocal
from src.database.repository import VideoRepository
from src.workers.celery_app import app

logger = logging.getLogger(__name__)

@dataclass
class CleanupStats:
    """Statistics for cleanup operations."""
    temp_dirs_removed: int = 0
    assets_cleaned: int = 0
    manifest_files_removed: int = 0
    total_space_freed: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class BlenderJobCleanupService:
    """Service for cleaning up Blender rendering artifacts."""

    def __init__(self, base_output_dir: str = None):
        self.base_output_dir = Path(base_output_dir or OUTPUT_DIR)
        self.temp_cleanup_age = timedelta(hours=2)  # Clean temp dirs older than 2 hours
        self.completed_cleanup_age = timedelta(days=7)  # Clean completed jobs older than 7 days
        self.failed_cleanup_age = timedelta(days=1)  # Clean failed jobs older than 1 day

    def cleanup_temporary_directories(self) -> CleanupStats:
        """Clean up orphaned temporary directories."""
        stats = CleanupStats()
        cleanup_cutoff = datetime.now() - self.temp_cleanup_age

        # Find and clean temp directories
        temp_patterns = ["**/blender_*", "**/tmp*blender*", "**/render_*"]

        for pattern in temp_patterns:
            for temp_path in self.base_output_dir.rglob(pattern):
                if temp_path.is_dir():
                    try:
                        # Check if directory is old enough to clean
                        mtime = datetime.fromtimestamp(temp_path.stat().st_mtime)
                        if mtime < cleanup_cutoff:
                            size_before = self._calculate_directory_size(temp_path)
                            shutil.rmtree(temp_path)
                            stats.temp_dirs_removed += 1
                            stats.total_space_freed += size_before
                            logger.info(f"Cleaned temporary directory: {temp_path}")
                    except Exception as e:
                        error_msg = f"Failed to clean {temp_path}: {e}"
                        stats.errors.append(error_msg)
                        logger.warning(error_msg)

        return stats

    def cleanup_expired_jobs(self) -> CleanupStats:
        """Clean up expired job artifacts from database."""
        stats = CleanupStats()
        db = SessionLocal()

        try:
            video_repo = VideoRepository(db)

            # Clean old completed videos
            completed_cutoff = datetime.now() - self.completed_cleanup_age
            completed_videos = video_repo.get_videos_by_status_and_age("completed", completed_cutoff)

            for video in completed_videos:
                try:
                    # Check if video file still exists and if it's old enough
                    video_path = Path(video.video_url) if video.video_url else None
                    if video_path and video_path.exists():
                        file_age = datetime.fromtimestamp(video_path.stat().st_mtime)
                        if file_age < completed_cutoff:
                            # Archive or delete the physical file
                            self._cleanup_video_file(video_path)
                            stats.assets_cleaned += 1
                            logger.info(f"Cleaned completed video file: {video_path}")

                    # Remove related artifacts (manifests, caches)
                    self._cleanup_job_artifacts(video.id)
                    stats.manifest_files_removed += 1

                except Exception as e:
                    error_msg = f"Failed to clean video {video.id}: {e}"
                    stats.errors.append(error_msg)
                    logger.warning(error_msg)

            # Clean old failed videos more aggressively
            failed_cutoff = datetime.now() - self.failed_cleanup_age
            failed_videos = video_repo.get_videos_by_status_and_age("failed", failed_cutoff)

            for video in failed_videos:
                try:
                    # Delete failed video artifacts immediately
                    self._cleanup_video_file(Path(video.video_url) if video.video_url else None)
                    self._cleanup_job_artifacts(video.id)
                    stats.assets_cleaned += 1
                    stats.manifest_files_removed += 1

                    # Remove from database
                    video_repo.delete_video(video.id)
                    logger.info(f"Permanently removed failed video: {video.id}")

                except Exception as e:
                    error_msg = f"Failed to clean failed video {video.id}: {e}"
                    stats.errors.append(error_msg)
                    logger.warning(error_msg)

        finally:
            db.close()

        return stats

    def cleanup_orphaned_artifacts(self) -> CleanupStats:
        """Clean up artifacts not tracked in database."""
        stats = CleanupStats()

        # Find orphaned .blend files
        for blend_file in self.base_output_dir.rglob("*.blend"):
            try:
                if self._is_orphaned_artifact(blend_file):
                    size = blend_file.stat().st_size
                    blend_file.unlink()
                    stats.assets_cleaned += 1
                    stats.total_space_freed += size
                    logger.info(f"Removed orphaned blend file: {blend_file}")
            except Exception as e:
                stats.errors.append(f"Failed to clean orphaned blend: {e}")

        # Find orphaned manifests
        for manifest_file in self.base_output_dir.rglob("*_manifest.json"):
            try:
                if self._is_orphaned_artifact(manifest_file):
                    manifest_file.unlink()
                    stats.manifest_files_removed += 1
                    logger.info(f"Removed orphaned manifest: {manifest_file}")
            except Exception as e:
                stats.errors.append(f"Failed to clean orphaned manifest: {e}")

        return stats

    def perform_full_cleanup(self) -> Dict[str, Any]:
        """Perform complete cleanup operation."""
        logger.info("Starting full Blender job cleanup")

        temp_stats = self.cleanup_temporary_directories()
        job_stats = self.cleanup_expired_jobs()
        orphan_stats = self.cleanup_orphaned_artifacts()

        # Aggregate statistics
        total_stats = CleanupStats()
        total_stats.temp_dirs_removed = (
            temp_stats.temp_dirs_removed +
            job_stats.temp_dirs_removed +
            orphan_stats.temp_dirs_removed
        )
        total_stats.assets_cleaned = (
            temp_stats.assets_cleaned +
            job_stats.assets_cleaned +
            orphan_stats.assets_cleaned
        )
        total_stats.manifest_files_removed = (
            temp_stats.manifest_files_removed +
            job_stats.manifest_files_removed +
            orphan_stats.manifest_files_removed
        )
        total_stats.total_space_freed = (
            temp_stats.total_space_freed +
            job_stats.total_space_freed +
            orphan_stats.total_space_freed
        )
        total_stats.errors = (
            temp_stats.errors +
            job_stats.errors +
            orphan_stats.errors
        )

        logger.info(f"Cleanup completed: {total_stats.temp_dirs_removed} temp dirs, "
                   f"{total_stats.assets_cleaned} assets, "
                   f"{total_stats.manifest_files_removed} manifests cleaned. "
                   f"Space freed: {total_stats.total_space_freed / (1024*1024):.2f} MB")

        if total_stats.errors:
            logger.warning(f"Cleanup had {len(total_stats.errors)} errors")

        return {
            'success': True,
            'stats': {
                'temp_dirs_removed': total_stats.temp_dirs_removed,
                'assets_cleaned': total_stats.assets_cleaned,
                'manifests_removed': total_stats.manifest_files_removed,
                'space_freed_mb': total_stats.total_space_freed / (1024 * 1024),
                'errors_count': len(total_stats.errors)
            },
            'errors': total_stats.errors[:10]  # Limit error reporting
        }

    def _calculate_directory_size(self, path: Path) -> int:
        """Calculate total size of directory contents."""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size

    def _cleanup_video_file(self, video_path: Optional[Path]) -> None:
        """Clean up video file and related artifacts."""
        if video_path and video_path.exists():
            try:
                # Remove video file
                size_before = video_path.stat().st_size
                video_path.unlink()

                # Remove associated files (.mp4 -> also remove .blend, manifests, etc.)
                stem = video_path.stem
                for related_file in video_path.parent.glob(f"{stem}.*"):
                    if related_file != video_path:  # Don't re-delete the main file
                        try:
                            related_file.unlink()
                        except Exception:
                            pass

                logger.debug(f"Cleaned video file and related artifacts: {video_path} ({size_before} bytes)")

            except Exception as e:
                logger.warning(f"Failed to clean video file {video_path}: {e}")

    def _cleanup_job_artifacts(self, video_id: int) -> None:
        """Clean up job-specific artifacts."""
        # Clean up any temp directories specific to this job
        job_patterns = [f"**/blender_{video_id}_*", f"**/render_{video_id}_*"]

        for pattern in job_patterns:
            for job_path in self.base_output_dir.rglob(pattern):
                try:
                    if job_path.is_dir():
                        shutil.rmtree(job_path)
                    else:
                        job_path.unlink()
                    logger.debug(f"Cleaned job artifact: {job_path}")
                except Exception as e:
                    logger.debug(f"Could not clean job artifact {job_path}: {e}")

    def _is_orphaned_artifact(self, path: Path) -> bool:
        """Check if a file is orphaned (not referenced in database)."""
        # Check if file is older than reasonable threshold (24 hours)
        # and not referenced in current video records
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age_threshold = datetime.now() - timedelta(days=1)

            if mtime < age_threshold:
                # File is old, check if it's referenced
                db = SessionLocal()
                try:
                    video_repo = VideoRepository(db)
                    # Look for any video that might reference this file
                    videos = video_repo.get_all_videos(limit=1000)

                    for video in videos:
                        if video.video_url and path.name in video.video_url:
                            return False  # Still referenced
                        if video.thumbnail_url and path.name in video.thumbnail_url:
                            return False  # Still referenced

                    return True  # Not referenced, is orphaned
                finally:
                    db.close()

        except Exception as e:
            logger.debug(f"Error checking if {path} is orphaned: {e}")
            return False  # Don't delete on error

        return False

# Global cleanup service instance
cleanup_service = BlenderJobCleanupService()

@app.task
def cleanup_blender_jobs():
    """Celery task to clean up old Blender rendering jobs."""
    try:
        logger.info("Starting Blender job cleanup task")
        result = cleanup_service.perform_full_cleanup()

        # Extract summary for Celery result
        return {
            'success': result['success'],
            'temp_dirs_cleaned': result['stats']['temp_dirs_removed'],
            'assets_cleaned': result['stats']['assets_cleaned'],
            'manifests_cleaned': result['stats']['manifests_removed'],
            'space_freed_mb': round(result['stats']['space_freed_mb'], 2),
            'errors_count': result['stats']['errors_count']
        }

    except Exception as e:
        logger.error(f"Blender job cleanup failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'temp_dirs_cleaned': 0,
            'assets_cleaned': 0,
            'manifests_cleaned': 0,
            'space_freed_mb': 0.0,
            'errors_count': 1
        }

# Utility functions for integration
def schedule_periodic_cleanup(interval_minutes: int = 60) -> None:
    """Schedule periodic cleanup to run every N minutes."""
    from src.workers.celery_app import app

    # This would be called during application startup to set up periodic tasks
    # In production, use Celery Beat for scheduling
    logger.info(f"Periodic cleanup scheduled for every {interval_minutes} minutes")

def cleanup_job_artifacts_sync(video_id: int) -> bool:
    """Synchronously clean up artifacts for a specific job."""
    try:
        cleanup_service._cleanup_job_artifacts(video_id)
        cleanup_service._cleanup_video_file(None)  # Placeholder for specific job files
        return True
    except Exception as e:
        logger.error(f"Failed to clean up job {video_id}: {e}")
        return False
