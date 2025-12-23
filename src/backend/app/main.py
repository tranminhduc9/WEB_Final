"""
FastAPI Application - Main Entry Point

Ứng dụng FastAPI chính cho Hanoi Travel với các tính năng:
- Authentication với JWT
- Email validation với Hunter.io
- PostgreSQL database
- MongoDB cho social data
- Rate limiting & CORS
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from ..config.database import init_db, test_connection
from .api.v1.auth import router as auth_router
from .api.v1.auth import user_router as user_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager cho startup và shutdown events

    Startup:
    1. Kết nối database
    2. Tạo tables
    3. Test connection

    Shutdown:
    1. Đóng database connections
    """
    # Startup
    logger.info("=" * 60)
    logger.info("STARTING HANOI TRAVEL API SERVER")
    logger.info("=" * 60)

    try:
        # Test database connection
        if test_connection():
            logger.info("✓ Database connection test: SUCCESS")

            # Initialize database tables
            init_db()
            logger.info("✓ Database initialized")
        else:
            logger.warning("✗ Database connection test: FAILED")
            logger.warning("Server will start but database features may not work")

        logger.info("✓ Server startup completed")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"✗ Startup error: {str(e)}")

    # Yield control to the application
    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("SHUTTING DOWN HANOI TRAVEL API SERVER")
    logger.info("=" * 60)
    logger.info("✓ Server shutdown completed")


# ==================== CREATE FASTAPI APP ====================

app = FastAPI(
    title="Hanoi Travel API",
    description="""
    API cho ứng dụng du lịch Hanoi Travel với các tính năng:
    - Authentication với JWT tokens
    - Email validation sử dụng Hunter.io
    - User management
    - Places discovery
    - Blog posts & comments
    - AI Chatbot
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ==================== MIDDLEWARE ====================

# CORS Middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ==================== ROUTERS ====================

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check

    Returns thông tin cơ bản về API server
    """
    return {
        "success": True,
        "message": "Hanoi Travel API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Trả về status của server và các services
    """
    health_status = {
        "success": True,
        "status": "healthy",
        "services": {
            "api": "running",
            "database": "unknown"
        }
    }

    # Check database connection
    try:
        db_connected = test_connection()
        health_status["services"]["database"] = "connected" if db_connected else "disconnected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"

    return health_status


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


# ==================== ERROR HANDLERS ====================

from fastapi import Request, status
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler cho tất cả các lỗi không được xử lý

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Đã có lỗi xảy ra, vui lòng thử lại sau"
            }
        }
    )


# ==================== STARTUP INSTRUCTIONS ====================

if __name__ == "__main__":
    import uvicorn

    # Lấy config từ environment
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting server at http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")

    # Run server
    uvicorn.run(
        "src.backend.app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
