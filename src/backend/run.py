"""
Backend Server Runner

Script này khởi động FastAPI backend server với đúng cấu trúc project.
Sử dụng script này thay vì chạy uvicorn trực tiếp.
"""

import sys
import os
from pathlib import Path

# Add src/backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

# IMPORTANT: Load environment tu root directory TRUOC
from config.load_env import load_environment, is_loaded

if not is_loaded():
    load_success = load_environment()
    if not load_success:
        print("WARNING: Failed to load .env file. Server may not work correctly.")
else:
    print("[OK] Environment loaded successfully")

import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to start the server"""

    # Get config from environment
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8080"))  # Default 8080
    reload = os.getenv("DEBUG", "false").lower() == "true"

    # Print startup info
    logger.info("=" * 70)
    logger.info("STARTING HANOIVIVU BACKEND SERVER")
    logger.info("=" * 70)
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[0]}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info("=" * 70)
    logger.info(f"Server URL: http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")
    logger.info("=" * 70)
    logger.info("Press CTRL+C to stop the server")
    logger.info("")

    try:
        # Start server với full logging
        uvicorn.run(
            "app.main:app",  # Module path from src/backend directory
            host=host,
            port=port,
            reload=reload,
            log_level="debug",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("SERVER SHUTTING DOWN")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

