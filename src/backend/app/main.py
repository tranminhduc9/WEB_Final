"""
FastAPI Application - Main Entry Point

Ứng dụng FastAPI chính cho Hanoi Travel với các tính năng:
- Authentication với JWT
- Email validation với Hunter.io
- PostgreSQL database
- MongoDB cho social data
- Rate limiting & CORS
"""

import logging
import os
import sys
from pathlib import Path

# IMPORTANT: Them thu muc cha vao sys.path TRUOC khi import relative modules
# app/main.py -> parent = src/backend
backend_dir = Path(__file__).parent.parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# IMPORTANT: Load environment tu root directory TRUOC khi import cac module khac
# Import centralized environment loader - dùng absolute import sau khi đã thêm sys.path
from config.load_env import load_environment, is_loaded

# Load environment variables from src/.env
if not is_loaded():
    load_success = load_environment()
    if not load_success:
        print("WARNING: Failed to load .env file. Some features may not work.")
else:
    print("[OK] Environment already loaded")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config.database import init_db, test_connection
from app.api.v1.auth import router as auth_router
from app.api.v1.logs import router as logs_router
from app.api.v1.places import router as places_router
from app.api.v1.users import router as users_router
from app.api.v1.posts import router as posts_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.upload import router as upload_router
from app.api.v1.admin import router as admin_router

# Import middleware setup
from middleware.setup import setup_middleware, setup_app
from middleware.config import config

# Configure logging
# Tạo logs directory nếu chưa tồn tại
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Custom UTF-8 handlers
class UTF8FileHandler(logging.FileHandler):
    """FileHandler with UTF-8 encoding"""
    def __init__(self, filename, *args, **kwargs):
        super().__init__(filename, encoding='utf-8', *args, **kwargs)

class UTF8StreamHandler(logging.StreamHandler):
    """StreamHandler with UTF-8 encoding - handles uvicorn reload safely"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Cấu hình logging - INFO level for cleaner output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        UTF8FileHandler(log_dir / "app.log"),
        logging.StreamHandler()
    ]
)

# Giảm noise từ các thư viện khác
for logger_name in ['uvicorn', 'uvicorn.access', 'sqlalchemy.engine', 'httpx', 'pymongo']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager cho sự kiện khởi động và tắt

    Khởi động:
    1. Kết nối database
    2. Tạo tables (nếu chưa tồn tại)
    3. Test kết nối
    4. Log thông tin cấu hình

    Tắt:
    1. Đóng các kết nối database
    """
    # Khởi động
    logger.info("=" * 60)
    logger.info("KHỞI ĐỘNG MÁY CHỦ HANOI TRAVEL API")
    logger.info("=" * 60)

    try:
        # Test kết nối database
        if test_connection():
            logger.info("[OK] Kiem tra ket noi database: THANH CONG")

            # Khởi tạo database tables
            init_db()
            logger.info("[OK] Da khoi tao database")
        else:
            logger.warning("[FAIL] Kiem tra ket noi database: THAT BAI")
            logger.warning("Máy chủ sẽ khởi động nhưng tính năng database có thể không hoạt động")

        logger.info("[OK] Hoan tat khoi dong may chu")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"[FAIL] Loi khoi dong: {str(e)}")

    # Chuyển điều khiển cho ứng dụng
    yield

    # Tắt
    logger.info("=" * 60)
    logger.info("TẮT MÁY CHỦ HANOI TRAVEL API")
    logger.info("=" * 60)
    logger.info("[OK] Da tat may chu")


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

# ==================== MIDDLEWARE SETUP ====================

# Setup toàn bộ middleware (Logging, CORS, Rate Limiting, Error Handling)
# Thứ tự middleware được áp dụng trong setup_middleware()
setup_middleware(app)

logger.info("Middleware configured successfully")
logger.info(f"  - Audit Logging: {config.ENABLE_AUDIT_LOG}")
logger.info(f"  - Rate Limiting: {config.RATE_LIMIT_ENABLED}")
logger.info(f"  - Search Logging: {config.ENABLE_SEARCH_LOGGING}")


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
app.include_router(logs_router, prefix="/api/v1")
app.include_router(places_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")

# ==================== STATIC FILES ====================
# Mount uploads directory để serve ảnh địa điểm
# Database lưu URLs: /static/uploads/places/place_1_0.jpg
uploads_path = Path(__file__).parent.parent.parent / "uploads"
if uploads_path.exists():
    # Mount /static/uploads để khớp với URLs trong database
    app.mount("/static/uploads", StaticFiles(directory=str(uploads_path)), name="static_uploads")
    # Mount /uploads cho các uploads mới
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
    logger.info(f"[OK] Mounted static files from: {uploads_path}")
else:
    logger.warning(f"[WARN] Uploads directory not found: {uploads_path}")


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
    port = int(os.getenv("BACKEND_PORT", "8080"))  # Default 8080 to match run.py
    reload = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting server at http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")

    # Chạy server
    uvicorn.run(
        "app.main:app",  # Đường dẫn module từ src/backend
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
