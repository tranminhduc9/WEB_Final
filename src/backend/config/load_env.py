"""
Centralized Environment Loader

Module này đảm bảo load file .env từ src/ directory
một cách nhất quán cho toàn bộ application.

IMPORTANT: Đây là module đầu tiên phải được import trong toàn bộ application.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def find_src_dir() -> Path:
    """
    Tìm src directory của project

    Src directory được xác định bằng cách:
    1. Từ file hiện tại (config/load_env.py), ngược lên 3 cấp: config/ -> backend/ -> src/
    2. Hoặc từ working directory khi chạy app

    Returns:
        Path: Src directory path
    """
    # Method 1: Từ file hiện tại
    # load_env.py nằm ở: src/backend/config/load_env.py
    # Đi lên 3 cấp: config/ -> backend/ -> src/
    current_file = Path(__file__).resolve()
    src_dir = current_file.parent.parent.parent  # config/backend/src

    # Verify src directory có .env file
    if not (src_dir / ".env").exists():
        # Method 2: Thử từ current working directory
        cwd = Path.cwd()

        # Nếu đang ở src/backend/, đi lên 1 cấp
        if cwd.name == "backend":
            src_dir = cwd.parent
        # Nếu đang ở src/, giữ nguyên
        elif cwd.name == "src":
            src_dir = cwd
        # Nếu đang ở WEB_Final/, vào src/
        elif (cwd / "src" / ".env").exists():
            src_dir = cwd / "src"
        # Fallback: dùng sys.path[0]
        else:
            sys_path = Path(sys.path[0])
            if (sys_path / "src" / ".env").exists():
                src_dir = sys_path / "src"
            elif (sys_path / ".env").exists():
                # sys.path[0] chính là src/
                src_dir = sys_path
            else:
                # Last resort: từ current file đi lên
                src_dir = current_file.parent.parent.parent

    return src_dir.resolve()


def load_environment(force_reload: bool = False) -> bool:
    """
    Load file .env từ src/ directory

    Args:
        force_reload: Force reload lại environment variables (mặc định: False)

    Returns:
        bool: True nếu load thành công, False nếu fail
    """
    try:
        # Tìm src directory
        src_dir = find_src_dir()
        env_file = src_dir / ".env"

        # Log thông tin
        logger.info(f"Src directory: {src_dir}")
        logger.info(f"Looking for .env at: {env_file}")

        # Kiểm tra file .env tồn tại
        if not env_file.exists():
            logger.error(f".env file not found at: {env_file}")
            logger.error("Please create .env file in src/ directory")
            return False

        # Load .env file
        # load_dotenv sẽ không overwrite các env vars đã được set trước đó
        # trừ khi force_reload=True
        load_dotenv(env_file, override=force_reload)

        # Verify key environment variables đã được load
        test_vars = [
            "HUNTER_IO_API_KEY",
            "DATABASE_URL",
            "JWT_SECRET_KEY"
        ]

        missing_vars = []
        for var in test_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)

        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        else:
            logger.info("✓ Environment variables loaded successfully")

        # Log một số key config (không log sensitive data)
        api_key = os.getenv("HUNTER_IO_API_KEY", "")
        if api_key:
            logger.info(f"✓ HUNTER_IO_API_KEY: {api_key[:10]}...{api_key[-4:]}")

        db_url = os.getenv("DATABASE_URL", "")
        if db_url:
            # Mask password in URL
            safe_url = db_url.split("@")[-1] if "@" in db_url else db_url
            logger.info(f"✓ DATABASE_URL: ...@{safe_url}")

        return True

    except Exception as e:
        logger.error(f"Error loading environment: {str(e)}")
        return False


def get_env_var(key: str, default: str = "") -> str:
    """
    Helper function để get environment variable

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        str: Environment variable value
    """
    value = os.getenv(key, default)
    return value


def is_loaded() -> bool:
    """
    Kiểm tra .env đã được load chưa

    Returns:
        bool: True nếu đã load, False nếu chưa
    """
    # Kiểm tra một key quan trọng
    return os.getenv("HUNTER_IO_API_KEY") is not None


# ==================== AUTO-LOAD ON IMPORT ====================
# Tự động load environment khi module này được import đầu tiên
# Nhưng chỉ load 1 lần (tránh reload nhiều lần)
_env_loaded = False

if not _env_loaded:
    _env_loaded = load_environment()

# Export cho các module khác sử dụng
__all__ = [
    "load_environment",
    "get_env_var",
    "is_loaded",
    "find_src_dir"
]
