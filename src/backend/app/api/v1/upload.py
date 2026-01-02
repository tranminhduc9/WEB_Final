"""
Upload API Routes

Module này định nghĩa API endpoint cho file upload:
- POST /upload - Upload files (images)

Refactored to use image_helpers for saving logic.
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from typing import Dict, Any, List
import logging

from middleware.auth import get_current_user
from middleware.response import success_response, error_response
from app.utils.image_helpers import save_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


# ==================== CONFIGURATION ====================

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== ENDPOINTS ====================

@router.post("", summary="Upload Files", status_code=201)
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(..., description="Files to upload"),
    folder: str = "misc",  # Optional: specify subfolder
    upload_type: str = "generic",  # Type: "place", "avatar", "post", or "generic"
    entity_id: str = None,  # ID of entity (place_id, user_id, post_id)
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload multiple files (images)
    
    Supported formats: PNG, JPG, JPEG, GIF, WEBP
    Max file size: 10MB per file
    
    Parameters:
        - folder: Subfolder to save in (default: "misc")
        - upload_type: Type of upload - "place", "avatar", "post", or "generic" (default: "generic")
        - entity_id: Required for typed uploads (place_id, user_id, post_id)
    
    Returns:
        - urls: List of full URLs for frontend display
        - relative_paths: List of relative paths for database storage
        - filenames: List of filenames
    """
    try:
        if not files:
            return error_response(
                message="Không có file nào được gửi",
                error_code="NO_FILES",
                status_code=400
            )
        
        # Validate upload_type
        valid_types = ["generic", "place", "avatar", "post"]
        if upload_type not in valid_types:
            return error_response(
                message=f"upload_type không hợp lệ. Chỉ chấp nhận: {', '.join(valid_types)}",
                error_code="INVALID_UPLOAD_TYPE",
                status_code=400
            )
        
        # For typed uploads, entity_id is required
        if upload_type != "generic" and not entity_id:
            return error_response(
                message=f"entity_id là bắt buộc cho upload_type='{upload_type}'",
                error_code="MISSING_ENTITY_ID",
                status_code=400
            )
        
        # Validate folder name to prevent directory traversal
        if ".." in folder or folder.startswith("/"):
            folder = "misc"
        
        # Auto-determine folder based on upload_type for typed uploads
        # This ensures images are saved to the correct subfolder
        type_to_folder = {
            "place": "places",
            "avatar": "avatars",
            "post": "posts"
        }
        if upload_type in type_to_folder:
            folder = type_to_folder[upload_type]
        
        uploaded_urls = []
        uploaded_paths = []
        uploaded_filenames = []
        errors = []
        
        for file in files:
            # Validate file
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: Định dạng không hỗ trợ")
                continue
            
            # Check file size before reading
            try:
                # Read file content to check size
                file_content = await file.read()
                file_size = len(file_content)
                
                if file_size > MAX_FILE_SIZE:
                    errors.append(f"{file.filename}: Kích thước vượt quá 10MB ({file_size // (1024*1024)}MB)")
                    continue
                
                # Reset file position for save_upload_file
                await file.seek(0)
            except Exception as e:
                errors.append(f"{file.filename}: Lỗi đọc file - {str(e)}")
                continue
            
            try:
                # Save using refactored helper
                result = await save_upload_file(
                    file, 
                    folder=folder,
                    upload_type=upload_type,
                    entity_id=entity_id
                )
                
                uploaded_urls.append(result["url"])
                uploaded_paths.append(result["relative_path"])
                uploaded_filenames.append(result["filename"])
                
            except Exception as e:
                errors.append(f"{file.filename}: Lỗi upload - {str(e)}")
        
        if not uploaded_urls:
            return error_response(
                message="Không upload được file nào",
                error_code="UPLOAD_FAILED",
                errors=errors,
                status_code=400
            )
        
        response_data = {
            "success": True,
            "message": f"Đã upload {len(uploaded_urls)} file",
            "urls": uploaded_urls,  # Full URLs for frontend
            "relative_paths": uploaded_paths,  # Relative paths for database
            "filenames": uploaded_filenames
        }
        if errors:
            response_data["errors"] = errors
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        return error_response(
            message=f"Lỗi upload file: {str(e)}",
            error_code="INTERNAL_ERROR",
            status_code=500
        )

