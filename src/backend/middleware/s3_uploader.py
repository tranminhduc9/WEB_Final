"""
S3 File Upload Module - AWS S3 Storage

Module này xử lý upload file lên AWS S3.
Sử dụng boto3 để tương tác với S3.

Được sử dụng bởi: image_helpers.py, file_upload.py

Environment variables required:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_BUCKET
- AWS_S3_REGION
"""

import os
import uuid
import mimetypes
from typing import Optional, Dict, Any
import logging

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from config.image_config import get_s3_config, get_image_url, ImageFolder

logger = logging.getLogger(__name__)


class S3FileUploader:
    """
    AWS S3 file upload service
    
    Upload và quản lý files trên AWS S3
    """
    
    def __init__(self):
        """
        Khởi tạo S3 client với credentials từ environment
        """
        self.config = get_s3_config()
        self.bucket = self.config["bucket"]
        self.region = self.config["region"]
        
        # Debug logging - check if config is loaded correctly
        access_key = self.config["access_key_id"]
        secret_key = self.config["secret_access_key"]
        
        logger.info(f"[S3 INIT] Bucket: {self.bucket}")
        logger.info(f"[S3 INIT] Region: {self.region}")
        logger.info(f"[S3 INIT] Access Key: {access_key[:5]}...{access_key[-4:] if len(access_key) > 9 else 'MISSING'}")
        logger.info(f"[S3 INIT] Secret Key: {'SET' if secret_key else 'MISSING'}")
        
        # Check for missing required config
        if not self.bucket:
            logger.error("[S3 INIT] AWS_S3_BUCKET is empty or not set!")
            self.s3_client = None
            return
            
        if not access_key or not secret_key:
            logger.error("[S3 INIT] AWS credentials are missing!")
            self.s3_client = None
            return
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=self.region
            )
            logger.info(f"[S3 INIT] S3 client initialized successfully for bucket: {self.bucket}")
        except NoCredentialsError:
            logger.error("[S3 INIT] AWS credentials not found")
            self.s3_client = None
        except Exception as e:
            logger.error(f"[S3 INIT] Failed to initialize S3 client: {str(e)}")
            self.s3_client = None
    
    def _get_content_type(self, filename: str) -> str:
        """
        Get MIME type for file
        
        Args:
            filename: Tên file
            
        Returns:
            MIME type string
        """
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    def _get_s3_key(self, folder: str, filename: str) -> str:
        """
        Generate S3 object key
        
        Format: static/uploads/{folder}/{filename}
        This matches the URL structure used in UPLOADS_BASE_URL
        
        Args:
            folder: Subfolder (places, avatars, posts)
            filename: Tên file
            
        Returns:
            S3 object key
        """
        return f"static/uploads/{folder}/{filename}"
    
    async def upload_image(
        self,
        file_content: bytes,
        filename: str,
        folder: str,
        max_size: int = 5 * 1024 * 1024  # 5MB
    ) -> Dict[str, Any]:
        """
        Upload image lên S3
        
        Args:
            file_content: Nội dung file (bytes)
            filename: Tên file gốc
            folder: Subfolder (places, avatars, posts)
            max_size: Kích thước tối đa (bytes)
            
        Returns:
            Dict với url, relative_path, filename
            
        Raises:
            ValueError: Nếu file quá lớn hoặc không hợp lệ
            Exception: Nếu upload thất bại
        """
        if not self.s3_client:
            raise Exception("S3 client not initialized. Check AWS credentials.")
        
        # Validate file size
        if len(file_content) > max_size:
            raise ValueError(f"File size exceeds maximum of {max_size / 1024 / 1024}MB")
        
        # Validate file extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        if ext not in allowed_extensions:
            raise ValueError(f"File type .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}")
        
        # Get S3 key and content type
        s3_key = self._get_s3_key(folder, filename)
        content_type = self._get_content_type(filename)
        
        # Debug logging before upload
        logger.info(f"[S3 UPLOAD] Starting upload...")
        logger.info(f"[S3 UPLOAD] Bucket: {self.bucket}")
        logger.info(f"[S3 UPLOAD] Key: {s3_key}")
        logger.info(f"[S3 UPLOAD] Content-Type: {content_type}")
        logger.info(f"[S3 UPLOAD] File size: {len(file_content)} bytes")
        
        try:
            # Upload to S3
            response = self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            
            logger.info(f"[S3 UPLOAD] Response: {response}")
            
            # Generate URL
            # Format: https://{bucket}.s3.{region}.amazonaws.com/static/uploads/{folder}/{filename}
            url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
            relative_path = f"{folder}/{filename}"
            
            logger.info(f"[S3 UPLOAD] SUCCESS: {s3_key} -> {url}")
            
            return {
                "success": True,
                "url": url,
                "relative_path": relative_path,
                "filename": filename,
                "folder": folder,
                "size": len(file_content),
                "s3_key": s3_key
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"S3 upload failed: {error_code} - {error_message}")
            raise Exception(f"S3 upload failed: {error_message}")
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise
    
    async def upload_place_image(
        self,
        file_content: bytes,
        filename: str,
        place_id: int,
        image_index: int = 0
    ) -> Dict[str, Any]:
        """
        Upload ảnh địa điểm lên S3
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            place_id: ID địa điểm
            image_index: Index của ảnh
            
        Returns:
            Upload result
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        custom_filename = f"place_{place_id}_{image_index}.{ext}"
        return await self.upload_image(file_content, custom_filename, "places")
    
    async def upload_avatar(
        self,
        file_content: bytes,
        filename: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Upload ảnh avatar lên S3
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            user_id: ID của user
            
        Returns:
            Upload result
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        custom_filename = f"avatar_{user_id}.{ext}"
        
        # Delete old avatar if exists (any extension)
        for old_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            if old_ext != ext:
                await self.delete_file("avatars", f"avatar_{user_id}.{old_ext}")
        
        return await self.upload_image(file_content, custom_filename, "avatars")
    
    async def upload_post_image(
        self,
        file_content: bytes,
        filename: str,
        entity_id: str,
        image_index: int = 0
    ) -> Dict[str, Any]:
        """
        Upload ảnh post lên S3
        
        Args:
            file_content: Nội dung file
            filename: Tên file gốc
            entity_id: Format {user_id}_{place_id} hoặc {user_id}_{timestamp}
            image_index: Index của ảnh
            
        Returns:
            Upload result
        """
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
        custom_filename = f"post_{entity_id}_{image_index}.{ext}"
        return await self.upload_image(file_content, custom_filename, "posts")
    
    async def delete_file(self, folder: str, filename: str) -> bool:
        """
        Xóa file khỏi S3
        
        Args:
            folder: Subfolder (places, avatars, posts)
            filename: Tên file
            
        Returns:
            True nếu xóa thành công hoặc file không tồn tại
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
        
        s3_key = self._get_s3_key(folder, filename)
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=s3_key
            )
            logger.info(f"Deleted from S3: {s3_key}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.warning(f"File not found in S3: {s3_key}")
                return True  # File doesn't exist, consider as success
            logger.error(f"S3 delete failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
            return False
    
    def file_exists(self, folder: str, filename: str) -> bool:
        """
        Kiểm tra file có tồn tại trên S3 không
        
        Args:
            folder: Subfolder
            filename: Tên file
            
        Returns:
            True nếu file tồn tại
        """
        if not self.s3_client:
            return False
        
        s3_key = self._get_s3_key(folder, filename)
        
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False


# Global S3 uploader instance - lazy initialization
# Will be created when first accessed via get_s3_uploader()
_s3_uploader_instance = None


def get_s3_uploader():
    """
    Get S3 uploader instance with lazy initialization.
    
    This ensures environment variables are loaded before creating the S3 client.
    
    Returns:
        S3FileUploader instance or None if S3 is not configured
    """
    global _s3_uploader_instance
    
    if _s3_uploader_instance is None:
        try:
            _s3_uploader_instance = S3FileUploader()
            if _s3_uploader_instance.s3_client is None:
                logger.warning("S3 client not initialized. Check AWS credentials.")
                _s3_uploader_instance = None
        except Exception as e:
            logger.warning(f"S3 uploader not available: {str(e)}")
            _s3_uploader_instance = None
    
    return _s3_uploader_instance


# Backward compatibility - create alias
# Note: This will be None until first access via get_s3_uploader()
s3_uploader = None
