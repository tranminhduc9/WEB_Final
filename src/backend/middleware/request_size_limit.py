"""
Request Size Limiting Middleware

Module này giới hạn kích thước request body để ngăn chặn:
- DoS attacks (gửi request cực lớn làm crash server)
- Slowloris attacks
- Memory exhaustion

Cấu hình mặc định:
- JSON body: 1MB
- Form data: 2MB  
- File upload: 5MB (từ .env MAX_FILE_SIZE)
"""

import os
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


# ==============================================
# CONFIGURATION
# ==============================================

class RequestSizeConfig:
    """Cấu hình giới hạn kích thước request"""
    
    # Giới hạn mặc định (bytes)
    MAX_JSON_BODY_SIZE = int(os.getenv("MAX_JSON_BODY_SIZE", str(1 * 1024 * 1024)))  # 1MB
    MAX_FORM_DATA_SIZE = int(os.getenv("MAX_FORM_DATA_SIZE", str(2 * 1024 * 1024)))  # 2MB
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(5 * 1024 * 1024)))  # 5MB
    
    # Content types
    JSON_CONTENT_TYPES = ["application/json", "text/json"]
    FORM_CONTENT_TYPES = ["application/x-www-form-urlencoded"]
    MULTIPART_CONTENT_TYPES = ["multipart/form-data"]
    
    # Endpoints được miễn trừ (upload files)
    EXEMPT_PATHS = [
        "/api/v1/upload",
        "/api/v1/users/avatar",
    ]
    
    # Enable/disable
    ENABLED = os.getenv("REQUEST_SIZE_LIMIT_ENABLED", "true").lower() == "true"


# ==============================================
# MIDDLEWARE
# ==============================================

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware giới hạn kích thước request body
    
    Features:
    - Kiểm tra Content-Length header
    - Giới hạn khác nhau cho JSON, form data, file upload
    - Exempt một số paths (upload endpoints)
    - Log requests bị reject
    """
    
    def __init__(self, app, config: RequestSizeConfig = None):
        super().__init__(app)
        self.config = config or RequestSizeConfig()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Kiểm tra kích thước request trước khi xử lý
        """
        if not RequestSizeConfig.ENABLED:
            return await call_next(request)
        
        # Bỏ qua GET, HEAD, OPTIONS requests (không có body)
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)
        
        # Bỏ qua exempt paths
        path = request.url.path
        if self._is_exempt_path(path):
            return await call_next(request)
        
        # Lấy Content-Length header
        content_length = request.headers.get("content-length")
        content_type = request.headers.get("content-type", "").lower()
        
        if content_length:
            try:
                body_size = int(content_length)
            except ValueError:
                # Invalid Content-Length header
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "message": "Content-Length header không hợp lệ",
                        "error_code": "INVALID_CONTENT_LENGTH"
                    }
                )
            
            # Xác định giới hạn dựa trên content type
            max_size = self._get_max_size(content_type, path)
            
            if body_size > max_size:
                # Log request bị reject
                client_ip = self._get_client_ip(request)
                logger.warning(
                    f"Request size exceeded: {body_size} bytes > {max_size} bytes | "
                    f"IP: {client_ip} | Path: {path} | Content-Type: {content_type}"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "success": False,
                        "message": f"Request quá lớn. Giới hạn: {max_size // (1024*1024)}MB",
                        "error_code": "REQUEST_TOO_LARGE",
                        "max_size_bytes": max_size,
                        "received_bytes": body_size
                    }
                )
        
        return await call_next(request)
    
    def _get_max_size(self, content_type: str, path: str) -> int:
        """
        Xác định giới hạn kích thước dựa trên content type và path
        """
        # File upload paths
        if any(exempt in path for exempt in RequestSizeConfig.EXEMPT_PATHS):
            return RequestSizeConfig.MAX_FILE_SIZE
        
        # Multipart (form với file)
        if any(ct in content_type for ct in RequestSizeConfig.MULTIPART_CONTENT_TYPES):
            return RequestSizeConfig.MAX_FILE_SIZE
        
        # Form data (không có file)
        if any(ct in content_type for ct in RequestSizeConfig.FORM_CONTENT_TYPES):
            return RequestSizeConfig.MAX_FORM_DATA_SIZE
        
        # JSON (default)
        return RequestSizeConfig.MAX_JSON_BODY_SIZE
    
    def _is_exempt_path(self, path: str) -> bool:
        """Kiểm tra path có được miễn trừ không"""
        return any(exempt in path for exempt in RequestSizeConfig.EXEMPT_PATHS)
    
    def _get_client_ip(self, request: Request) -> str:
        """Lấy IP address của client"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host if request.client else "unknown"


# ==============================================
# UTILITY FUNCTIONS
# ==============================================

def format_bytes(size_bytes: int) -> str:
    """Format bytes thành human-readable string"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# Log configuration on import
logger.info("Request Size Limiting Configuration:")
logger.info(f"  - Enabled: {RequestSizeConfig.ENABLED}")
logger.info(f"  - Max JSON Body: {format_bytes(RequestSizeConfig.MAX_JSON_BODY_SIZE)}")
logger.info(f"  - Max Form Data: {format_bytes(RequestSizeConfig.MAX_FORM_DATA_SIZE)}")
logger.info(f"  - Max File Upload: {format_bytes(RequestSizeConfig.MAX_FILE_SIZE)}")
logger.info(f"  - Exempt Paths: {RequestSizeConfig.EXEMPT_PATHS}")


# ==============================================
# EXPORTS
# ==============================================

__all__ = [
    'RequestSizeConfig',
    'RequestSizeLimitMiddleware',
    'format_bytes',
]
