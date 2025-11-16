"""
File management service for secure upload and download operations.
"""
import os
import uuid
import mimetypes
import hashlib
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import logging
from urllib.parse import quote

from ..database.connection import SessionLocal
from ..database.repository import AssetRepository
from ..database.schemas import AssetCreate

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass

class FileStorageError(Exception):
    """Custom exception for file storage errors."""
    pass

class SecureFileManager:
    """Secure file manager for handling uploads and downloads."""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or "/app/uploads"
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        self.allowed_extensions = {
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            '.pdf', '.txt', '.doc', '.docx'
        }
        self.allowed_mime_types = {
            'video/mp4', 'video/avi', 'video/quicktime', 'video/webm',
            'image/png', 'image/jpeg', 'image/gif', 'image/bmp',
            'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac',
            'application/pdf', 'text/plain', 'application/msword'
        }
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure storage directory exists."""
        try:
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create storage directory: {str(e)}")
            raise FileStorageError(f"Storage directory creation failed: {str(e)}")
    
    def validate_file(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Validate uploaded file."""
        try:
            # Check file size
            if len(file_data) == 0:
                raise FileValidationError("File is empty")
            
            if len(file_data) > self.max_file_size:
                raise FileValidationError(f"File size exceeds maximum allowed size ({self.max_file_size // 1024 // 1024}MB)")
            
            # Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                raise FileValidationError(f"File extension '{file_ext}' not allowed")
            
            # Check MIME type
            if content_type not in self.allowed_mime_types:
                # Try to guess MIME type from content
                guessed_type, _ = mimetypes.guess_type(filename)
                if guessed_type not in self.allowed_mime_types:
                    raise FileValidationError(f"Content type '{content_type}' not allowed")
            
            # Calculate file hash for deduplication
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename, file_hash)
            
            return {
                "valid": True,
                "filename": unique_filename,
                "original_filename": filename,
                "file_size": len(file_data),
                "content_type": content_type,
                "file_extension": file_ext,
                "file_hash": file_hash,
                "file_path": os.path.join(self.storage_path, unique_filename)
            }
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            raise FileValidationError(f"File validation failed: {str(e)}")
    
    def generate_unique_filename(self, original_filename: str, file_hash: str) -> str:
        """Generate unique filename to prevent conflicts."""
        name_parts = Path(original_filename).stem, Path(original_filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_hash = file_hash[:8]
        return f"{name_parts[0]}_{timestamp}_{short_hash}{name_parts[1]}"
    
    def store_file(self, file_data: bytes, validation_result: Dict[str, Any]) -> str:
        """Store file in the storage system."""
        try:
            file_path = validation_result["file_path"]
            
            # Write file to storage
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"File stored successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"File storage error: {str(e)}")
            raise FileStorageError(f"Failed to store file: {str(e)}")
    
    def create_asset_record(
        self,
        user_id: int,
        validation_result: Dict[str, Any],
        project_id: Optional[int] = None,
        video_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create asset record in database."""
        try:
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                
                asset_data = AssetCreate(
                    filename=validation_result["filename"],
                    original_filename=validation_result["original_filename"],
                    file_type=validation_result["file_extension"].lstrip('.'),
                    mime_type=validation_result["content_type"],
                    project_id=project_id,
                    video_id=video_id
                )
                
                asset = asset_repo.create_asset(
                    asset_data,
                    file_path=validation_result["file_path"],
                    file_size=validation_result["file_size"]
                )
                
                # Update with additional metadata
                metadata = {
                    "file_hash": validation_result["file_hash"],
                    "upload_timestamp": datetime.now().isoformat(),
                    "file_size_mb": round(validation_result["file_size"] / 1024 / 1024, 2)
                }
                
                asset_repo.update_asset_processing_status(
                    asset.id,
                    is_processed=False,
                    metadata=str(metadata)
                )
                
                return {
                    "asset_id": asset.id,
                    "filename": asset.filename,
                    "file_path": asset.file_path,
                    "file_size": asset.file_size,
                    "file_type": asset.file_type,
                    "mime_type": asset.mime_type,
                    "upload_timestamp": metadata["upload_timestamp"]
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Asset record creation error: {str(e)}")
            raise
    
    def download_file(self, asset_id: int, user_id: int) -> Tuple[bytes, str, str]:
        """Download file for authenticated user."""
        try:
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                asset = asset_repo.get_asset(asset_id)
                
                if not asset:
                    raise FileNotFoundError(f"Asset {asset_id} not found")
                
                # Check if user has access to this asset
                if not self._user_has_access(asset, user_id, db):
                    raise PermissionError("User does not have access to this file")
                
                # Read file from storage
                if not os.path.exists(asset.file_path):
                    raise FileNotFoundError(f"File not found on storage: {asset.file_path}")
                
                with open(asset.file_path, 'rb') as f:
                    file_data = f.read()
                
                logger.info(f"File downloaded successfully: {asset.filename}")
                return file_data, asset.mime_type, asset.filename
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"File download error: {str(e)}")
            raise
    
    def _user_has_access(self, asset, user_id: int, db) -> bool:
        """Check if user has access to the asset."""
        from ..database.repository import ProjectRepository
        
        # Public access for public projects
        if asset.project_id:
            project_repo = ProjectRepository(db)
            project = project_repo.get_project(asset.project_id)
            if project and project.is_public:
                return True
        
        # User owns the project
        if asset.project_id:
            project_repo = ProjectRepository(db)
            project = project_repo.get_project(asset.project_id)
            if project and project.user_id == user_id:
                return True
        
        # Check if user owns the video
        if asset.video_id:
            from ..database.repository import VideoRepository
            video_repo = VideoRepository(db)
            video = video_repo.get_video(asset.video_id)
            if video:
                project_repo = ProjectRepository(db)
                project = project_repo.get_project(video.project_id)
                if project and project.user_id == user_id:
                    return True
        
        return False
    
    def delete_file(self, asset_id: int, user_id: int) -> bool:
        """Delete file and asset record."""
        try:
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                asset = asset_repo.get_asset(asset_id)
                
                if not asset:
                    raise FileNotFoundError(f"Asset {asset_id} not found")
                
                # Check permissions
                if not self._user_has_access(asset, user_id, db):
                    raise PermissionError("User does not have permission to delete this file")
                
                # Delete physical file
                if os.path.exists(asset.file_path):
                    os.remove(asset.file_path)
                
                # Delete database record (would need to implement delete in repository)
                # asset_repo.delete_asset(asset_id)  # This method would need to be added
                
                logger.info(f"File deleted successfully: {asset.filename}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            raise
    
    def get_file_info(self, asset_id: int, user_id: int) -> Dict[str, Any]:
        """Get file information for authenticated user."""
        try:
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                asset = asset_repo.get_asset(asset_id)
                
                if not asset:
                    raise FileNotFoundError(f"Asset {asset_id} not found")
                
                # Check access permissions
                if not self._user_has_access(asset, user_id, db):
                    raise PermissionError("User does not have access to this file")
                
                return {
                    "asset_id": asset.id,
                    "filename": asset.filename,
                    "original_filename": asset.original_filename,
                    "file_size": asset.file_size,
                    "file_type": asset.file_type,
                    "mime_type": asset.mime_type,
                    "file_path": asset.file_path,
                    "is_processed": asset.is_processed,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None,
                    "project_id": asset.project_id,
                    "video_id": asset.video_id
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"File info retrieval error: {str(e)}")
            raise
    
    def list_user_files(self, user_id: int, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files accessible to user."""
        try:
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                
                if project_id:
                    assets = asset_repo.get_assets_by_project(project_id)
                else:
                    # Get all assets from user's projects
                    from ..database.repository import ProjectRepository
                    project_repo = ProjectRepository(db)
                    projects = project_repo.get_projects_by_user(user_id)
                    
                    all_assets = []
                    for project in projects:
                        assets = asset_repo.get_assets_by_project(project.id)
                        all_assets.extend(assets)
                    assets = all_assets
                
                # Filter accessible assets
                accessible_assets = []
                for asset in assets:
                    if self._user_has_access(asset, user_id, db):
                        accessible_assets.append({
                            "asset_id": asset.id,
                            "filename": asset.filename,
                            "original_filename": asset.original_filename,
                            "file_size": asset.file_size,
                            "file_type": asset.file_type,
                            "mime_type": asset.mime_type,
                            "is_processed": asset.is_processed,
                            "created_at": asset.created_at.isoformat() if asset.created_at else None,
                            "project_id": asset.project_id,
                            "video_id": asset.video_id
                        })
                
                return accessible_assets
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"File listing error: {str(e)}")
            raise
    
    def cleanup_old_files(self, older_than_days: int = 30) -> Dict[str, int]:
        """Clean up files older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            cleaned_count = 0
            error_count = 0
            
            db = SessionLocal()
            try:
                asset_repo = AssetRepository(db)
                
                # Get all assets created before cutoff date
                # This would require a method in AssetRepository
                # For now, we'll implement basic cleanup logic
                
                db.close()
                
                # Clean up files from storage directory
                storage_path = Path(self.storage_path)
                for file_path in storage_path.rglob('*'):
                    if file_path.is_file():
                        try:
                            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_mtime < cutoff_date:
                                file_path.unlink()
                                cleaned_count += 1
                        except Exception as e:
                            logger.error(f"Error cleaning up file {file_path}: {str(e)}")
                            error_count += 1
                
                logger.info(f"Cleanup completed: {cleaned_count} files cleaned, {error_count} errors")
                return {"cleaned": cleaned_count, "errors": error_count}
                
            finally:
                if db:
                    db.close()
                
        except Exception as e:
            logger.error(f"File cleanup error: {str(e)}")
            raise
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        try:
            storage_path = Path(self.storage_path)
            
            total_size = 0
            file_count = 0
            
            for file_path in storage_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "total_files": file_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "storage_path": self.storage_path,
                "max_file_size_mb": self.max_file_size / 1024 / 1024,
                "allowed_extensions": list(self.allowed_extensions)
            }
            
        except Exception as e:
            logger.error(f"Storage stats error: {str(e)}")
            raise

# Global file manager instance
file_manager = SecureFileManager()