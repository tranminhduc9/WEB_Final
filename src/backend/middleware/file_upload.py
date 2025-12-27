"""
File Upload Middleware

Module này xử lý upload file lên cloud storage (Cloudinary)
với validation và security checks.
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import logging
import aiofiles
import tempfile

logger = logging.getLogger(__name__)


class FileUploadConfig:
    """Cấu hình cho file upload"""

    # File size limits (bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB

    # Allowed file types
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        'image/webp': ['.webp']
    }

    ALLOWED_VIDEO_TYPES = {
        'video/mp4': ['.mp4'],
        'video/avi': ['.avi'],
        'video/mov': ['.mov']
    }

    # Upload destinations
    DEFAULT_FOLDER = "hanoi-travel"
    AVATAR_FOLDER = "avatars"
    POST_FOLDER = "posts"
    PLACE_FOLDER = "places"


class CloudinaryUploader:
    """
    Cloudinary upload service

    Cung cấp các phương thức upload file lên Cloudinary
    với validation và transformation.
    """

    def __init__(self, cloud_name: str = None, api_key: str = None, api_secret: str = None):
        """
        Khởi tạo Cloudinary uploader

        Args:
            cloud_name: Cloudinary cloud name
            api_key: Cloudinary API key
            api_secret: Cloudinary API secret
        """
        self.cloud_name = cloud_name or os.getenv("CLOUDINARY_CLOUD_NAME")
        self.api_key = api_key or os.getenv("CLOUDINARY_API_KEY")
        self.api_secret = api_secret or os.getenv("CLOUDINARY_API_SECRET")

        # Initialize Cloudinary client if credentials available
        if self.cloud_name and self.api_key and self.api_secret:
            try:
                import cloudinary
                import cloudinary.uploader
                import cloudinary.api

                cloudinary.config(
                    cloud_name=self.cloud_name,
                    api_key=self.api_key,
                    api_secret=self.api_secret
                )

                self.cloudinary = cloudinary
                self.uploader = cloudinary.uploader
                self.api = cloudinary.api
                self.is_configured = True
                logger.info("Cloudinary client initialized successfully")

            except ImportError:
                logger.warning("Cloudinary SDK not installed. Using fallback mode.")
                self.is_configured = False
            except Exception as e:
                logger.error(f"Failed to initialize Cloudinary: {str(e)}")
                self.is_configured = False
        else:
            logger.warning("Cloudinary credentials not configured")
            self.is_configured = False

    async def upload_image(
        self,
        file: UploadFile,
        folder: str = None,
        transformations: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Upload image lên Cloudinary

        Args:
            file: UploadFile object
            folder: Thư mục đích
            transformations: Cloudinary transformations

        Returns:
            Dict: {url, public_id, secure_url}

        Raises:
            HTTPException: Nếu upload thất bại
        """
        # Validate file
        self._validate_image_file(file)

        if self.is_configured:
            return await self._upload_to_cloudinary(file, folder, transformations, "image")
        else:
            return await self._upload_locally(file, folder, "image")

    async def upload_video(
        self,
        file: UploadFile,
        folder: str = None
    ) -> Dict[str, str]:
        """
        Upload video lên Cloudinary

        Args:
            file: UploadFile object
            folder: Thư mục đích

        Returns:
            Dict: {url, public_id, secure_url}

        Raises:
            HTTPException: Nếu upload thất bại
        """
        # Validate file
        self._validate_video_file(file)

        if self.is_configured:
            return await self._upload_to_cloudinary(file, folder, None, "video")
        else:
            return await self._upload_locally(file, folder, "video")

    def _validate_image_file(self, file: UploadFile):
        """
        Validate image file

        Args:
            file: UploadFile object

        Raises:
            HTTPException: Nếu file không hợp lệ
        """
        # Check file size
        if hasattr(file, 'size') and file.size:
            if file.size > FileUploadConfig.MAX_IMAGE_SIZE:
                from .response import file_too_large_response
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": f"File không được vượt quá {FileUploadConfig.MAX_IMAGE_SIZE // (1024*1024)}MB",
                        "data": None,
                        "error_code": "FILE_001"
                    }
                )

        # Check file extension
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            allowed_extensions = []
            for extensions in FileUploadConfig.ALLOWED_IMAGE_TYPES.values():
                allowed_extensions.extend(extensions)

            if ext not in allowed_extensions:
                from .response import invalid_file_type_response
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": f"Chỉ hỗ trợ các định dạng: {', '.join(allowed_extensions)}",
                        "data": None,
                        "error_code": "FILE_002"
                    }
                )

        # Check MIME type
        if file.content_type not in FileUploadConfig.ALLOWED_IMAGE_TYPES:
            from .response import invalid_file_type_response
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": f"Chỉ hỗ trợ các định dạng: {', '.join(['jpg', 'jpeg', 'png'])}",
                    "data": None,
                    "error_code": "FILE_002"
                }
            )

    def _validate_video_file(self, file: UploadFile):
        """
        Validate video file

        Args:
            file: UploadFile object

        Raises:
            HTTPException: Nếu file không hợp lệ
        """
        # Check file size
        if hasattr(file, 'size') and file.size:
            if file.size > FileUploadConfig.MAX_VIDEO_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video size exceeds {FileUploadConfig.MAX_VIDEO_SIZE // (1024*1024)}MB limit"
                )

        # Check file extension
        if file.filename:
            ext = os.path.splitext(file.filename)[1].lower()
            allowed_extensions = []
            for extensions in FileUploadConfig.ALLOWED_VIDEO_TYPES.values():
                allowed_extensions.extend(extensions)

            if ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video type not allowed. Allowed: {', '.join(allowed_extensions)}"
                )

        # Check MIME type
        if file.content_type not in FileUploadConfig.ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Video type not supported. Allowed: {list(FileUploadConfig.ALLOWED_VIDEO_TYPES.keys())}"
            )

    async def _upload_to_cloudinary(
        self,
        file: UploadFile,
        folder: str,
        transformations: Dict[str, Any],
        resource_type: str
    ) -> Dict[str, str]:
        """
        Upload file lên Cloudinary

        Args:
            file: UploadFile object
            folder: Thư mục đích
            transformations: Cloudinary transformations
            resource_type: Type of resource (image/video)

        Returns:
            Dict: Upload result

        Raises:
            HTTPException: Nếu upload thất bại
        """
        try:
            # Generate unique public_id
            public_id = f"{folder or FileUploadConfig.DEFAULT_FOLDER}/{uuid.uuid4()}"

            # Prepare upload options
            upload_options = {
                "public_id": public_id,
                "resource_type": resource_type,
                "folder": folder or FileUploadConfig.DEFAULT_FOLDER
            }

            # Add transformations for images
            if resource_type == "image" and transformations:
                upload_options["transformation"] = transformations

            # Read file content
            content = await file.read()
            await file.seek(0)  # Reset file pointer

            # Upload to Cloudinary
            result = self.uploader.upload(
                content,
                **upload_options
            )

            return {
                "url": result.get("url"),
                "secure_url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "resource_type": result.get("resource_type"),
                "format": result.get("format"),
                "size": result.get("bytes")
            }

        except Exception as e:
            logger.error(f"Cloudinary upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {str(e)}"
            )

    async def _upload_locally(
        self,
        file: UploadFile,
        folder: str,
        resource_type: str
    ) -> Dict[str, str]:
        """
        Upload file locally (fallback)

        Args:
            file: UploadFile object
            folder: Thư mục đích
            resource_type: Type of resource

        Returns:
            Dict: Local upload result
        """
        try:
            # Create upload directory if not exists
            upload_dir = os.path.join("uploads", folder or FileUploadConfig.DEFAULT_FOLDER)
            os.makedirs(upload_dir, exist_ok=True)

            # Generate unique filename
            ext = os.path.splitext(file.filename or "")[1]
            filename = f"{uuid.uuid4()}{ext}"
            file_path = os.path.join(upload_dir, filename)

            # Save file locally
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            # Return local URL
            local_url = f"/uploads/{folder or FileUploadConfig.DEFAULT_FOLDER}/{filename}"

            return {
                "url": local_url,
                "secure_url": local_url,
                "public_id": filename,
                "resource_type": resource_type,
                "format": ext[1:],  # Remove dot
                "local_path": file_path
            }

        except Exception as e:
            logger.error(f"Local upload failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {str(e)}"
            )

    async def delete_file(self, public_id: str, resource_type: str = "image") -> bool:
        """
        Xóa file khỏi Cloudinary

        Args:
            public_id: Public ID của file
            resource_type: Loại resource

        Returns:
            bool: True nếu xóa thành công
        """
        if not self.is_configured:
            # Fallback: delete local file
            try:
                file_path = os.path.join("uploads", public_id)
                if os.path.exists(file_path):
                    os.remove(file_path)
                return True
            except Exception as e:
                logger.error(f"Failed to delete local file: {str(e)}")
                return False

        try:
            result = self.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception as e:
            logger.error(f"Failed to delete file from Cloudinary: {str(e)}")
            return False


# Global uploader instance
uploader = CloudinaryUploader()


# Utility functions
async def upload_avatar(file: UploadFile, user_id: int) -> Dict[str, str]:
    """
    Upload avatar cho user

    Args:
        file: UploadFile object
        user_id: ID của user

    Returns:
        Dict: Upload result
    """
    folder = f"{FileUploadConfig.AVATAR_FOLDER}/{user_id}"

    # Transformations cho avatar
    transformations = {
        "width": 300,
        "height": 300,
        "crop": "fill",
        "gravity": "face",
        "quality": "auto"
    }

    return await uploader.upload_image(file, folder, transformations)


async def upload_post_image(file: UploadFile, post_id: int) -> Dict[str, str]:
    """
    Upload image cho bài viết

    Args:
        file: UploadFile object
        post_id: ID của bài viết

    Returns:
        Dict: Upload result
    """
    folder = f"{FileUploadConfig.POST_FOLDER}/{post_id}"

    # Transformations cho post image
    transformations = {
        "width": 1200,
        "height": 630,
        "crop": "fill",
        "quality": "auto"
    }

    return await uploader.upload_image(file, folder, transformations)


async def upload_place_image(file: UploadFile, place_id: int) -> Dict[str, str]:
    """
    Upload image cho địa điểm

    Args:
        file: UploadFile object
        place_id: ID của địa điểm

    Returns:
        Dict: Upload result
    """
    folder = f"{FileUploadConfig.PLACE_FOLDER}/{place_id}"

    # Transformations cho place image
    transformations = {
        "width": 800,
        "height": 600,
        "crop": "fill",
        "quality": "auto"
    }

    return await uploader.upload_image(file, folder, transformations)


def validate_multiple_files(
    files: List[UploadFile],
    max_files: int = 5,
    max_total_size: int = 20 * 1024 * 1024  # 20MB
):
    """
    Validate multiple files upload

    Args:
        files: Danh sách UploadFile objects
        max_files: Số file tối đa
        max_total_size: Tổng size tối đa

    Raises:
        HTTPException: Nếu validation failed
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {max_files} files allowed"
        )

    total_size = 0
    for file in files:
        if hasattr(file, 'size') and file.size:
            total_size += file.size

    if total_size > max_total_size:
        raise HTTPException(
            status_code=400,
            detail=f"Total file size exceeds {max_total_size // (1024*1024)}MB limit"
        )

    # Validate individual files
    for file in files:
        uploader._validate_image_file(file)