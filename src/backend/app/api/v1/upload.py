"""
Upload API Routes

Module này định nghĩa API endpoint cho file upload:
- POST /upload - Upload files (images)

Swagger v1.0.5 Compatible - Cloudinary Integration
"""

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from typing import Dict, Any, List
import logging
import os

from middleware.auth import get_current_user
from middleware.response import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


# ==================== CONFIGURATION ====================

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def upload_to_cloudinary(file: UploadFile) -> str:
    """
    Upload file to Cloudinary
    Returns: URL of uploaded file
    """
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        
        # Read file content
        content = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder="hanoi_travel",
            resource_type="image"
        )
        
        return result.get("secure_url")
        
    except Exception as e:
        logger.error(f"Cloudinary upload error: {str(e)}")
        raise


async def save_file_locally(file: UploadFile) -> str:
    """
    Fallback: Save file locally if Cloudinary not configured
    Returns: Local URL
    """
    import uuid
    from pathlib import Path
    
    # Create uploads directory
    upload_dir = Path(__file__).parent.parent.parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = upload_dir / filename
    
    # Save file
    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)
    
    # Return local URL
    return f"/uploads/{filename}"


# ==================== ENDPOINTS ====================

@router.post("", summary="Upload Files", status_code=201)
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(..., description="Files to upload"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload multiple files (images)
    
    Supported formats: PNG, JPG, JPEG, GIF, WEBP
    Max file size: 10MB per file
    
    Returns:
        urls: List of uploaded file URLs
    """
    try:
        if not files:
            return error_response(
                message="Không có file nào được gửi",
                error_code="NO_FILES",
                status_code=400
            )
        
        uploaded_urls = []
        errors = []
        
        for file in files:
            # Validate file
            if not allowed_file(file.filename):
                errors.append(f"{file.filename}: Định dạng không hỗ trợ")
                continue
            
            # Check file size
            content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            if len(content) > MAX_FILE_SIZE:
                errors.append(f"{file.filename}: File quá lớn (max 10MB)")
                continue
            
            try:
                # Try Cloudinary first
                if os.getenv("CLOUDINARY_CLOUD_NAME"):
                    url = await upload_to_cloudinary(file)
                else:
                    # Fallback to local storage
                    url = await save_file_locally(file)
                
                uploaded_urls.append(url)
                
            except Exception as e:
                errors.append(f"{file.filename}: Lỗi upload - {str(e)}")
        
        if not uploaded_urls:
            return error_response(
                message="Không upload được file nào",
                error_code="UPLOAD_FAILED",
                errors=errors,
                status_code=400
            )
        
        response_data = {"urls": uploaded_urls}
        if errors:
            response_data["errors"] = errors
        
        return success_response(
            message=f"Đã upload {len(uploaded_urls)} file",
            data=response_data
        )
        
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        return error_response(
            message="Lỗi upload file",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF UPLOAD ROUTES ====================
