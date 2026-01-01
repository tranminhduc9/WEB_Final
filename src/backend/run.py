"""
Backend Server Runner

Script này khởi động FastAPI backend server.
Sử dụng script này thay vì chạy uvicorn trực tiếp.

Usage:
    python run.py                    # Dev mode (127.0.0.1:8080)
    python run.py --prod             # Production mode (0.0.0.0:8080)
    python run.py --port 8000        # Custom port
    python run.py --reload           # Enable hot reload
    python run.py --help             # Show help
"""

import sys
import os
import argparse
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


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Hanoivivu Backend Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                 # Dev mode (127.0.0.1:8080)
  python run.py --prod          # Production mode (0.0.0.0:8080)
  python run.py --port 8000     # Custom port
  python run.py --reload        # Enable hot reload for development
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host to bind (default: 127.0.0.1, or 0.0.0.0 with --prod)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind (default: 8080 or BACKEND_PORT env var)"
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Production mode: bind to 0.0.0.0 and disable reload"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Log level (default: info)"
    )
    
    return parser.parse_args()


def main():
    """Main function to start the server"""
    args = parse_args()
    
    # Determine host
    if args.host:
        host = args.host
    elif args.prod:
        host = "0.0.0.0"
    else:
        host = os.getenv("BACKEND_HOST", "127.0.0.1")
    
    # Determine port
    if args.port:
        port = args.port
    else:
        port = int(os.getenv("BACKEND_PORT", "8080"))
    
    # Determine reload
    reload = args.reload and not args.prod
    
    # Print startup info
    mode = "PRODUCTION" if args.prod else "DEVELOPMENT"
    logger.info("=" * 70)
    logger.info(f"STARTING HANOIVIVU BACKEND SERVER ({mode})")
    logger.info("=" * 70)
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    logger.info(f"Log level: {args.log_level}")
    logger.info("=" * 70)
    logger.info(f"Server URL: http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")
    logger.info(f"ReDoc: http://{host}:{port}/redoc")
    logger.info("=" * 70)
    logger.info("Press CTRL+C to stop the server")
    logger.info("")

    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=args.log_level,
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
