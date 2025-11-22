"""
File management API routes for secure upload and download operations.
"""

import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.auth.security import get_current_user
from src.database.connection import get_db
from src.services.file_manager import (
    FileStorageError,
    FileValidationError,
    file_manager,
)
from src.services.task_manager import task_manager

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    video_id: Optional[int] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file securely."""
    try:
        # Read file content
        file_content = await file.read()

        # Validate file
        validation_result = file_manager.validate_file(
            file_content, file.filename, file.content_type
        )

        # Store file
        file_path = file_manager.store_file(file_content, validation_result)

        # Create asset record
        asset_record = file_manager.create_asset_record(
            current_user["user_id"],
            validation_result,
            project_id=project_id,
            video_id=video_id,
        )

        return {
            "message": "File uploaded successfully",
            "asset": asset_record,
            "validation": {
                "file_size": validation_result["file_size"],
                "file_hash": validation_result["file_hash"],
                "file_type": validation_result["file_type"],
            },
        }

    except FileValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        )


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    project_id: Optional[int] = Form(None),
    video_id: Optional[int] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload multiple files at once."""
    if len(files) > 10:  # Limit number of files
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 files allowed per upload",
        )

    uploaded_assets = []
    errors = []

    for file in files:
        try:
            # Read file content
            file_content = await file.read()

            # Validate file
            validation_result = file_manager.validate_file(
                file_content, file.filename, file.content_type
            )

            # Store file
            file_path = file_manager.store_file(file_content, validation_result)

            # Create asset record
            asset_record = file_manager.create_asset_record(
                current_user["user_id"],
                validation_result,
                project_id=project_id,
                video_id=video_id,
            )

            uploaded_assets.append(asset_record)

        except FileValidationError as e:
            errors.append({"filename": file.filename, "error": str(e)})
        except FileStorageError as e:
            errors.append({"filename": file.filename, "error": str(e)})
        except Exception as e:
            errors.append({"filename": file.filename, "error": "Upload failed"})

    return {
        "message": f"Upload completed. {len(uploaded_assets)} files uploaded, {len(errors)} errors.",
        "uploaded_assets": uploaded_assets,
        "errors": errors,
    }


@router.get("/download/{asset_id}")
async def download_file(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a file."""
    try:
        file_data, mime_type, filename = file_manager.download_file(
            asset_id, current_user["user_id"]
        )

        return StreamingResponse(
            iter([file_data]),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(file_data)),
            },
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Download failed"
        )


@router.get("/files")
async def list_files(
    project_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List files accessible to user."""
    try:
        files = file_manager.list_user_files(
            current_user["user_id"], project_id=project_id
        )

        # Apply pagination
        paginated_files = files[skip : skip + limit]

        return {
            "files": paginated_files,
            "total": len(files),
            "skip": skip,
            "limit": limit,
        }

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"File listing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files",
        )


@router.get("/files/{asset_id}")
async def get_file_info(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get file information."""
    try:
        file_info = file_manager.get_file_info(asset_id, current_user["user_id"])
        return file_info

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"File info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file information",
        )


@router.delete("/files/{asset_id}")
async def delete_file(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a file."""
    try:
        success = file_manager.delete_file(asset_id, current_user["user_id"])

        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file",
            )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"File deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file",
        )


@router.post("/files/{asset_id}/process")
async def process_uploaded_file(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process an uploaded file (generate thumbnails, extract metadata, etc.)."""
    try:
        # Get file info to verify access
        file_info = file_manager.get_file_info(asset_id, current_user["user_id"])

        # Queue processing task
        task_id = task_manager.queue_video_upload_processing(
            asset_id=asset_id,
            video_id=file_info.get("video_id"),
            user_id=current_user["user_id"],
        )

        return {
            "message": "File processing started",
            "task_id": task_id,
            "asset_id": asset_id,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"File processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start file processing",
        )


@router.get("/stats")
async def get_file_storage_stats(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get file storage statistics."""
    try:
        stats = file_manager.get_storage_stats()

        # Add user-specific stats
        user_files = file_manager.list_user_files(current_user["user_id"])
        user_total_size = sum(f["file_size"] for f in user_files)

        stats.update(
            {
                "user_files_count": len(user_files),
                "user_total_size_mb": round(user_total_size / 1024 / 1024, 2),
                "user_file_types": list(set(f["file_type"] for f in user_files)),
            }
        )

        return stats

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Storage stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get storage statistics",
        )


@router.post("/cleanup")
async def cleanup_old_files(
    older_than_days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
):
    """Clean up old files (admin users only in real implementation)."""
    try:
        # In a real implementation, check if user is admin
        result = file_manager.cleanup_old_files(older_than_days)

        return {
            "message": f"Cleanup completed",
            "files_cleaned": result["cleaned"],
            "errors": result["errors"],
        }

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Cleanup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cleanup failed"
        )
