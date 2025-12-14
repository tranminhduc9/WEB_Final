"""
Middleware Setup Configuration
Cấu hình và khởi tạo toàn bộ middleware theo đúng thứ tự cho API contract
"""

import os
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle management cho FastAPI app
    - Khởi tạo connections
    - Setup middleware
    - Cleanup khi shutdown
    """
    # Startup
    logger.info("🚀 Starting Hanoi Travel API...")

    # Initialize audit log directory
    if config.ENABLE_AUDIT_LOG and config.AUDIT_LOG_FILE:
        os.makedirs(os.path.dirname(config.AUDIT_LOG_FILE), exist_ok=True)
        logger.info(f"📝 Audit log enabled: {config.AUDIT_LOG_FILE}")

    # Initialize upload directory
    if config.UPLOAD_PATH:
        os.makedirs(config.UPLOAD_PATH, exist_ok=True)
        logger.info(f"📁 Upload directory: {config.UPLOAD_PATH}")

    # Log configuration summary
    logger.info("⚙️  Configuration loaded:")
    logger.info(f"   • Environment: {config.ENVIRONMENT}")
    logger.info(f"   • Rate Limiting: {'Enabled' if config.RATE_LIMIT_ENABLED else 'Disabled'}")
    logger.info(f"   • Audit Logging: {'Enabled' if config.ENABLE_AUDIT_LOG else 'Disabled'}")
    logger.info(f"   • Search Logging: {'Enabled' if config.ENABLE_SEARCH_LOGGING else 'Disabled'}")
    logger.info(f"   • File Upload: {'Cloudinary' if config.CLOUDINARY_CLOUD_NAME else 'Local'}")
    logger.info(f"   • Email: {'Configured' if config.SMTP_USERNAME else 'Not configured'}")

    logger.info("✅ Hanoi Travel API started successfully!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Hanoi Travel API...")


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

    # 8. Rate Limiting Middleware
    if config.RATE_LIMIT_ENABLED:
        use_redis = config.RATE_LIMIT_STORAGE == "redis"
        rate_limiter = RateLimitMiddleware(use_redis=use_redis)
        app.add_middleware(rate_limiter.__class__)
        logger.info(f"   ✅ Rate limiting enabled (storage: {config.RATE_LIMIT_STORAGE})")

    # Note: Authentication, Validation middleware được thêm
    # ở từng endpoint level qua decorators/dependencies

    logger.info("🎉 Middleware chain setup completed!")


def setup_app(app: FastAPI) -> FastAPI:
    """
    Setup complete FastAPI app với middleware và lifecycle

    Args:
        app: FastAPI application instance

    Returns:
        FastAPI: Configured application
    """
    # Set lifespan handler
    app.router.lifespan_context = lifespan

    # Setup middleware chain
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
    Create và configure FastAPI app với toàn bộ middleware

    Returns:
        FastAPI: Configured application
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
    """Get current user dependency"""
    from .auth import get_current_user
    return get_current_user


def require_admin():
    """Require admin role dependency"""
    from .auth import require_roles
    return require_roles(["admin"])


def require_moderator():
    """Require moderator or admin role dependency"""
    from .auth import require_roles
    return require_roles(["admin", "moderator"])


def rate_limit_custom(limit_type: str = "medium", window_size: int = 60):
    """Custom rate limit decorator"""
    from .rate_limit import rate_limit
    return rate_limit(limit_type=limit_type, window_size=window_size)


def audit_action(action_type: str, message: str):
    """Audit action decorator"""
    from .audit_log import audit_action, ActionType, LogLevel
    action_type_enum = getattr(ActionType, action_type.upper(), ActionType.API_CALL)
    return audit_action(action_type_enum, message, LogLevel.INFO)


# Export commonly used items
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