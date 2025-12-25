"""
Middleware Setup Configuration
Cấu hình và khởi tạo toàn bộ middleware theo đúng thứ tự cho API contract
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

if sys.platform == 'win32':
    import io
    # Force UTF-8 cho sys.stdout/stderr (Python 3.7+ compatible)
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from .config import config
from .cors import setup_cors, add_security_headers
from .error_handler import ErrorMiddleware
from .rate_limit import RateLimitMiddleware
from .audit_log import AuditMiddleware, audit_logger
from .search_logging import SearchLoggingMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware thêm request ID vào tất cả requests
    """

    async def dispatch(self, request: Request, call_next):
        import uuid
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware đo thời gian xử lý request
    """

    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response


# Lưu ý: Lifespan handler đã được chuyển sang app/main.py
# để tránh duplicate và tập trung logic khởi tạo database tại một nơi
# Middleware này chỉ chịu trách nhiệm setup middleware chain


def setup_middleware(app: FastAPI) -> None:
    """
    Setup toàn bộ middleware theo đúng thứ tự cho API contract

    Thứ tự thực thi (từ ngoài vào trong):
    1. CORS - Xử lý cross-origin requests
    2. Security Headers - Thêm headers bảo mật
    3. Request ID - Thêm ID theo dõi request
    4. Timing - Đo thời gian xử lý
    5. Error Handler - Bắt và xử lý errors
    6. Audit Log - Ghi log hành động người dùng
    7. Search Logging - Ghi log tìm kiếm
    8. Rate Limiting - Giới hạn tốc độ
    9. Authentication/Authorization - Kiểm tra JWT/Roles
    10. Validation - Validate input data
    11. Business Logic - Xử lý API endpoints

    Args:
        app: FastAPI application instance
    """
    logger.info("🔧 Setting up middleware chain...")

    # 1. CORS Middleware
    if config.CORS_ORIGINS:
        cors_config = config.get_cors_config()
        app.add_middleware(
            CORSMiddleware,
            **cors_config
        )
        logger.info(f"   ✅ CORS configured for: {', '.join(config.CORS_ORIGINS)}")

    # 2. Security Headers (cho production)
    if config.ENVIRONMENT == "production":
        add_security_headers(app)
        logger.info("   ✅ Security headers added")

    # 3. Request ID Middleware
    app.add_middleware(RequestIDMiddleware)
    logger.info("   ✅ Request ID middleware added")

    # 4. Timing Middleware
    app.add_middleware(TimingMiddleware)
    logger.info("   ✅ Timing middleware added")

    # 5. Error Handler Middleware (quan trọng nhất)
    app.add_middleware(ErrorMiddleware)
    logger.info("   ✅ Error handling middleware added")

    # 6. Audit Logging Middleware
    if config.ENABLE_AUDIT_LOG:
        app.add_middleware(AuditMiddleware, audit_logger=audit_logger)
        logger.info("   ✅ Audit logging middleware added")

    # 7. Search Logging Middleware
    if config.ENABLE_SEARCH_LOGGING:
        app.add_middleware(SearchLoggingMiddleware)
        logger.info("   ✅ Search logging middleware added")


    # 8. Rate Limiting
    # Note: Rate limiting được áp dụng qua FastAPI dependencies
    # Sử dụng dependencies=[Depends(apply_rate_limit)] ở từng endpoint
    if config.RATE_LIMIT_ENABLED:
        logger.info(f"   ✅ Rate limiting enabled (using dependency injection pattern)")
        logger.info(f"      Storage: {config.RATE_LIMIT_STORAGE}")
        logger.info(f"      Applied to auth endpoints via dependencies=[Depends(apply_rate_limit)]")

    # Note: Authentication, Validation middleware được thêm
    # ở từng endpoint level qua decorators/dependencies

    logger.info("🎉 Middleware chain setup completed!")


def setup_app(app: FastAPI) -> FastAPI:
    """
    Thiết lập hoàn chỉnh FastAPI app với middleware

    Args:
        app: FastAPI application instance

    Returns:
        FastAPI: Ứng dụng đã được cấu hình

    Lưu ý:
        - Lifespan handler được đặt trong app/main.py
        - Function này chỉ thiết lập middleware chain
    """
    # Thiết lập middleware chain
    setup_middleware(app)

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler cho unexpected errors"""
        from .error_handler import error_handler
        from fastapi.responses import JSONResponse

        api_error = error_handler.handle_exception(exc)
        return JSONResponse(
            status_code=api_error.status_code,
            content=api_error.to_dict()
        )

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "environment": config.ENVIRONMENT,
            "version": config.API_VERSION,
            "features": {
                "rate_limiting": config.RATE_LIMIT_ENABLED,
                "audit_logging": config.ENABLE_AUDIT_LOG,
                "search_logging": config.ENABLE_SEARCH_LOGGING,
                "file_upload": bool(config.CLOUDINARY_CLOUD_NAME),
                "email": bool(config.SMTP_USERNAME),
                "chatbot": config.CHATBOT_ENABLED
            }
        }

    # Add API info endpoint
    @app.get("/api/info")
    async def api_info():
        """API information endpoint"""
        return {
            "name": "Hanoi Travel API",
            "version": config.API_VERSION,
            "description": "API for Hanoi Travel Application",
            "endpoints": {
                "authentication": "/api/v1/auth/*",
                "places": "/api/v1/places/*",
                "posts": "/api/v1/posts/*",
                "users": "/api/v1/users/*",
                "chatbot": "/api/v1/chatbot/*",
                "admin": "/api/v1/admin/*"
            },
            "documentation": "/docs",
            "rate_limits": config.get_rate_limit_config(),
            "middleware": {
                "cors": True,
                "error_handling": True,
                "rate_limiting": config.RATE_LIMIT_ENABLED,
                "audit_logging": config.ENABLE_AUDIT_LOG,
                "search_logging": config.ENABLE_SEARCH_LOGGING
            }
        }

    logger.info("🚀 FastAPI application configured successfully!")
    return app


def create_fastapi_app() -> FastAPI:
    """
    Tạo và cấu hình FastAPI app với toàn bộ middleware

    Returns:
        FastAPI: Ứng dụng đã được cấu hình
    """
    app = FastAPI(
        title="Hanoi Travel API",
        description="API for Hanoi Travel Application",
        version=config.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    return setup_app(app)


# Utility functions cho endpoint integration
def require_auth():
    """Lấy dependency cho user hiện tại"""
    from .auth import get_current_user
    return get_current_user


def require_admin():
    """Yêu cầu vai trò admin"""
    from .auth import require_roles
    return require_roles(["admin"])


def require_moderator():
    """Yêu cầu vai trò moderator hoặc admin"""
    from .auth import require_roles
    return require_roles(["admin", "moderator"])


def rate_limit_custom(limit_type: str = "medium", window_size: int = 60):
    """Decorator tùy chỉnh giới hạn tốc độ"""
    from .rate_limit import rate_limit
    return rate_limit(limit_type=limit_type, window_size=window_size)


def audit_action(action_type: str, message: str):
    """Decorator ghi log hành động"""
    from .audit_log import audit_action, ActionType, LogLevel
    action_type_enum = getattr(ActionType, action_type.upper(), ActionType.API_CALL)
    return audit_action(action_type_enum, message, LogLevel.INFO)


# Export các mục thường dùng
__all__ = [
    "create_fastapi_app",
    "setup_app",
    "setup_middleware",
    "config",
    "require_auth",
    "require_admin",
    "require_moderator",
    "rate_limit_custom",
    "audit_action"
]