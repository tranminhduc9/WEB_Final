"""
File Upload Module - Local Storage Only

Module này xử lý upload file lên local storage (uploads folder).
Sử dụng UPLOADS_BASE_URL từ .env để tạo URLs cho ảnh.

Cấu trúc thư mục:
- uploads/places/     - Ảnh địa điểm
- uploads/avatars/    - Ảnh đại diện người dùng
- uploads/posts/      - Ảnh bài viết

Được sử dụng bởi: upload.py, users.py
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from config.image_config import get_image_url, ImageFolder

logger = logging.getLogger(__name__)


class LocalFileUploader:
    """
    Local file upload service
    
    Upload và quản lý files trên local storage
    """
    
    def __init__(self, upload_base_path: Optional[str] = None):
        """
        Khởi tạo Local file uploader
        
        Args:
            upload_base_path: Base path cho uploads folder
        """
        # Get upload base path (src/static/uploads) - use absolute path
        if upload_base_path:
            self.upload_base_path = Path(upload_base_path)
        else:
            # Default: src/static/uploads using absolute path
            current_file = Path(__file__).resolve()
            # src/backend/middleware/file_upload.py -> src/backend/middleware -> src/backend -> src
            src_dir = current_file.parent.parent.parent
            self.upload_base_path = src_dir / "static" / "uploads"

        
        # Create base upload directory if not exists
        self.upload_base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subfolders
        self.folders = {
            ImageFolder.PLACES: self.upload_base_path / "places",
            ImageFolder.AVATARS: self.upload_base_path / "avatars",
            ImageFolder.POSTS: self.upload_base_path / "posts"
        }
        
        for folder_path in self.folders.values():
            folder_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Local file uploader initialized at: {self.upload_base_path}")
    
    async def upload_image(
        self,
        file_content: bytes,
        filename: str,
        folder: ImageFolder,
        max_size: int = 5 * 1024 * 1024  # 5MB
    ) -> Dict[str, Any]:
        """
        Upload image lên local storage
        
        Args:
            file_content: Nội dung file (bytes)
            filename: Tên file gốc
            folder: ImageFolder enum (PLACES, AVATARS, POSTS)
            max_size: Kích thước tối đa (bytes)
            
        Returns:
            Dict với url, path, filename
            
        Raises:
            ValueError: Nếu file quá lớn hoặc không hợp lệ
        """
        # Validate file size
        if len(file_content) > max_size:
            raise ValueError(f"File size exceeds maximum of {max_size / 1024 / 1024}MB")
        
        # Validate file extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        if ext not in allowed_extensions:
            raise ValueError(f"File type .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}")
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Get folder path
        folder_path = self.folders[folder]
        file_path = folder_path / unique_filename
        
        try:
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Generate URL using centralized config
            url = get_image_url(folder, unique_filename)
            
            logger.info(f"Uploaded file: {unique_filename} to {folder.value}/")
            
            return {
                "success": True,
                "url": url,
                "filename": unique_filename,
                "folder": folder.value,
                "path": str(file_path),
                "size": len(file_content)
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            # Clean up if file was partially written
            if file_path.exists():
                file_path.unlink()
            raise
    
    async def upload_place_image(
        self,
        file_content: bytes,
        filename: str,
        place_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Upload ảnh địa điểm
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            place_id: ID địa điểm (optional, để đặt tên file)
            
        Returns:
            Upload result
        """
        # If place_id provided, use naming convention
        if place_id:
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
            # Count existing images for this place
            existing = list(self.folders[ImageFolder.PLACES].glob(f"place_{place_id}_*.{ext}"))
            index = len(existing)
            custom_filename = f"place_{place_id}_{index}.{ext}"
            
            # Write with custom name
            file_path = self.folders[ImageFolder.PLACES] / custom_filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            url = get_image_url(ImageFolder.PLACES, custom_filename)
            
            return {
                "success": True,
                "url": url,
                "filename": custom_filename,
                "folder": "places",
                "path": str(file_path),
                "size": len(file_content)
            }
        else:
            return await self.upload_image(file_content, filename, ImageFolder.PLACES)
    
    async def upload_avatar(
        self,
        file_content: bytes,
        filename: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Upload ảnh avatar cho user
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            user_id: ID của user
            
        Returns:
            Upload result
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        
        # Delete old avatar if exists
        old_avatars = list(self.folders[ImageFolder.AVATARS].glob(f"avatar_{user_id}*"))
        for old_avatar in old_avatars:
            old_avatar.unlink()
        
        # Custom filename with user_id
        custom_filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = self.folders[ImageFolder.AVATARS] / custom_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        url = get_image_url(ImageFolder.AVATARS, custom_filename)
        
        return {
            "success": True,
            "url": url,
            "filename": custom_filename,
            "folder": "avatars",
            "path": str(file_path),
            "size": len(file_content)
        }
    
    async def upload_post_image(
        self,
        file_content: bytes,
        filename: str,
        post_id: str
    ) -> Dict[str, Any]:
        """
        Upload ảnh cho post
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            post_id: MongoDB ObjectId của post
            
        Returns:
            Upload result
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        
        # Count existing images for this post
        existing = list(self.folders[ImageFolder.POSTS].glob(f"post_{post_id}_*.{ext}"))
        index = len(existing)
        
        custom_filename = f"post_{post_id}_{index}.{ext}"
        file_path = self.folders[ImageFolder.POSTS] / custom_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        url = get_image_url(ImageFolder.POSTS, custom_filename)
        
        return {
            "success": True,
            "url": url,
            "filename": custom_filename,
            "folder": "posts",
            "path": str(file_path),
            "size": len(file_content)
        }
    
    async def delete_file(self, folder: ImageFolder, filename: str) -> bool:
        """
        Xóa file khỏi local storage
        
        Args:
            folder: ImageFolder enum
            filename: Tên file
            
        Returns:
            True nếu xóa thành công
        """
        try:
            file_path = self.folders[folder] / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {filename} from {folder.value}/")
                return True
            else:
                logger.warning(f"File not found: {filename} in {folder.value}/")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def get_file_path(self, folder: ImageFolder, filename: str) -> Optional[Path]:
        """
        Lấy path của file
        
        Args:
            folder: ImageFolder enum
            filename: Tên file
            
        Returns:
            Path nếu file tồn tại, None nếu không
        """
        file_path = self.folders[folder] / filename
        return file_path if file_path.exists() else None


# Global uploader instance
uploader = LocalFileUploader()