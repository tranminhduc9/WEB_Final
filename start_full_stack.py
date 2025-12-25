"""
Full Stack Startup Script

Script này tự động khởi động TẤT CẢ services:
1. Docker Data DB (port 5433)
2. Docker Auth DB (port 5432)
3. Backend Server (port 8080)
4. Frontend Server (port 5173)
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
import requests
from threading import Thread

# ⚠️ QUAN TRỌNG: Set UTF-8 encoding cho Windows console
# Phải set trước khi import các module khác
if sys.platform == 'win32':
    import io
    # Force UTF-8 cho stdout/stderr
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Set environment variable
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
BACKEND_DIR = SRC_DIR / "backend"
FRONTEND_DIR = SRC_DIR / "frontend"
DOCKER_COMPOSE_FILE = SRC_DIR / "docker-compose.yml"

BACKEND_URL = "http://127.0.0.1:8080"
FRONTEND_URL = "http://localhost:5173"

processes = []
NPM_COMMAND = "npm"  # Default npm command, will be updated by check_npm()


# ==================== DOCKER MANAGEMENT ====================

def check_docker() -> bool:
    """Kiểm tra Docker có đang chạy không"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"✅ Docker detected: {result.stdout.strip()}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Docker not available: {e}")
        return False


def check_container_running(container_name: str) -> bool:
    """Kiểm tra container có đang chạy không"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container_name in result.stdout
    except Exception:
        return False


def start_docker_databases():
    """Khởi động Docker databases"""
    logger.info("=" * 70)
    logger.info("STEP 1: STARTING DOCKER DATABASES")
    logger.info("=" * 70)

    os.chdir(SRC_DIR)

    data_db_running = check_container_running("travel_db_container")

    if data_db_running:
        logger.info("✅ All Docker databases already running")
        return True

    try:
        logger.info("🚀 Starting Docker databases...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=300  # Tăng lên 5 phút cho pull images
        )

        if result.returncode != 0:
            logger.error(f"❌ Failed to start docker-compose: {result.stderr}")
            return False

        logger.info("✅ Docker databases started successfully")
        logger.info("⏳ Waiting for databases to be ready...")
        time.sleep(10)

        return True

    except Exception as e:
        logger.error(f"❌ Error starting Docker databases: {e}")
        return False


# ==================== BACKEND MANAGEMENT ====================

def stream_output(process, name):
    """Stream output từ process ra console real-time"""
    try:
        while True:
            # Đọc line với encoding errors handling
            line = process.stdout.readline()

            # EOF check
            if not line:
                # Check if process ended
                if process.poll() is not None:
                    break
                time.sleep(0.1)
                continue

            # Decode với UTF-8 và error handling
            try:
                # Cố gắng decode UTF-8
                decoded_line = line.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback: decode với errors='replace'
                decoded_line = line.decode('utf-8', errors='replace')

            # In ra console (đã có UTF-8 wrapper)
            print(f"[{name}] {decoded_line}", end='', flush=True)

    except Exception as e:
        # Ignore errors khi process terminated
        if process.poll() is None:  # Process still running
            logger.error(f"Error reading {name} output: {e}")


def start_backend():
    """Khởi động Backend server"""
    logger.info("=" * 70)
    logger.info("STEP 3: STARTING BACKEND SERVER")
    logger.info("=" * 70)

    os.chdir(BACKEND_DIR)
    sys.path.insert(0, str(BACKEND_DIR))

    try:
        logger.info("🚀 Starting Backend server...")
        logger.info(f"   URL: {BACKEND_URL}")
        logger.info(f"   Swagger: {BACKEND_URL}/docs")

        # Start backend with uvicorn
        # NOTE: --reload bị bỏ vì gây conflict với middleware chain (request timeout)
        # Nếu cần hot-reload trong development, chạy riêng: cd src/backend && uvicorn app.main:app --reload
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app",
               "--host", "127.0.0.1", "--port", "8080",
               "--log-level", "info"]

        # QUAN TRỌNG: Mở subprocess với binary mode để raw bytes
        # Sau đó decode manually với error handling
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,  # Binary mode (raw bytes)
            stderr=subprocess.STDOUT
        )

        # Start thread để stream output ra console
        output_thread = Thread(target=stream_output, args=(process, "BACKEND"), daemon=True)
        output_thread.start()

        processes.append(("Backend", process))
        logger.info("✅ Backend server started")
        logger.info("⏳ Waiting for backend to be ready...")
        time.sleep(5)

        return True

    except Exception as e:
        logger.error(f"❌ Error starting backend: {e}")
        return False


# ==================== FRONTEND MANAGEMENT ====================

def check_node() -> bool:
    """Kiểm tra Node.js có được cài đặt không"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"✅ Node.js detected: {result.stdout.strip()}")
            return True
        return False
    except Exception:
        return False


def check_npm() -> bool:
    """Kiểm tra npm có được cài đặt không"""
    # Trên Windows, npm thường là npm.cmd
    npm_commands = ["npm.cmd", "npm"] if sys.platform == "win32" else ["npm"]
    
    for npm_cmd in npm_commands:
        try:
            result = subprocess.run(
                [npm_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ npm detected: {result.stdout.strip()}")
                # Lưu npm command để dùng sau
                global NPM_COMMAND
                NPM_COMMAND = npm_cmd
                return True
        except FileNotFoundError:
            continue
        except Exception as e:
            logger.error(f"❌ Error checking {npm_cmd}: {type(e).__name__}: {e}")
            continue
    
    # Nếu không tìm thấy npm, thử tìm full path
    logger.error("❌ npm command not found in PATH")
    logger.error("   Trying to locate npm...")
    
    try:
        # Thử dùng 'where' command trên Windows
        if sys.platform == "win32":
            result = subprocess.run(
                ["where", "npm"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                npm_path = result.stdout.strip().split('\n')[0]
                logger.info(f"   Found npm at: {npm_path}")
                NPM_COMMAND = npm_path
                return True
    except Exception as e:
        logger.error(f"   Could not locate npm: {e}")
    
    logger.error("   npm may not be installed or not in PATH")
    logger.error("   Please ensure npm is installed and accessible")
    return False


def check_frontend_deps() -> bool:
    """Kiểm tra frontend dependencies đã cài chưa"""
    node_modules = FRONTEND_DIR / "node_modules"
    return node_modules.exists()


def install_frontend_deps():
    """Cài đặt frontend dependencies"""
    logger.info("📦 Installing frontend dependencies...")
    os.chdir(FRONTEND_DIR)

    try:
        result = subprocess.run(
            [NPM_COMMAND, "install"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode != 0:
            logger.error(f"❌ Failed to install dependencies: {result.stderr}")
            return False

        logger.info("✅ Dependencies installed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        return False


def start_frontend():
    """Khởi động Frontend server"""
    logger.info("=" * 70)
    logger.info("STEP 4: STARTING FRONTEND SERVER")
    logger.info("=" * 70)

    # Check Node.js and npm
    if not check_node():
        logger.error("❌ Node.js is not installed")
        logger.info("💡 Install Node.js from: https://nodejs.org/")
        return False

    if not check_npm():
        logger.error("❌ npm is not installed")
        return False

    os.chdir(FRONTEND_DIR)

    # Check dependencies
    if not check_frontend_deps():
        logger.warning("⚠️  Frontend dependencies not found")
        if not install_frontend_deps():
            return False

    try:
        logger.info("🚀 Starting Frontend server...")
        logger.info(f"   URL: {FRONTEND_URL}")

        # Start frontend with npm - binary mode để raw bytes
        cmd = [NPM_COMMAND, "run", "dev"]

        # Mở subprocess với binary mode
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,  # Binary mode (raw bytes)
            stderr=subprocess.STDOUT
        )

        # Start thread để stream output ra console
        output_thread = Thread(target=stream_output, args=(process, "FRONTEND"), daemon=True)
        output_thread.start()

        processes.append(("Frontend", process))
        logger.info("✅ Frontend server started")
        logger.info("⏳ Waiting for frontend to be ready...")
        time.sleep(5)

        return True

    except Exception as e:
        logger.error(f"❌ Error starting frontend: {e}")
        return False


# ==================== SERVICE MONITORING ====================

def print_log_header():
    """In header cho phần monitoring"""
    print("\n" + "=" * 70)
    print(" 📊 LOGS STREAMING - REAL-TIME OUTPUT")
    print("=" * 70)
    print(" 📌 Backend logs: [BACKEND] prefix")
    print(" 📌 Frontend logs: [FRONTEND] prefix")
    print(" 💡 Tips:")
    print("    - Mọi HTTP requests sẽ được log")
    print("    - Check logs/audit.log và logs/app.log để xem chi tiết")
    print("    - Press CTRL+C để stop tất cả services")
    print("=" * 70 + "\n")


def monitor_services():
    """Giám sát output từ các processes"""
    logger.info("=" * 70)
    logger.info("📊 SERVICE MONITORING")
    logger.info("=" * 70)

    for name, process in processes:
        logger.info(f"📌 {name}: PID {process.pid}")

    logger.info("=" * 70)
    logger.info("✅ All services are running!")
    logger.info("=" * 70)
    logger.info(f"🔗 Frontend: {FRONTEND_URL}")
    logger.info(f"🔗 Backend:  {BACKEND_URL}")
    logger.info(f"🔗 Swagger:  {BACKEND_URL}/docs")
    logger.info(f"🔗 pgAdmin:  http://localhost:5050")
    logger.info(f"📁 Logs dir: src/backend/logs/")
    logger.info("=" * 70)

    # In header cho log streaming
    print_log_header()

    try:
        # Keep running until interrupted
        while True:
            # Check if any process died
            dead_processes = []
            for name, process in processes:
                if process.poll() is not None:
                    dead_processes.append(name)
                    logger.error(f"❌ {name} process died unexpectedly!")

            if dead_processes:
                logger.error(f"❌ Dead processes: {', '.join(dead_processes)}")
                logger.info("💡 Check logs above for errors")

            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("SHUTTING DOWN ALL SERVICES")
        logger.info("=" * 70)


def cleanup():
    """Dừng tất cả processes"""
    for name, process in processes:
        try:
            logger.info(f"🛑 Stopping {name}...")
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"✅ {name} stopped")
        except Exception as e:
            logger.warning(f"⚠️  Error stopping {name}: {e}")
            process.kill()


# ==================== MAIN ====================

def main():
    """Main function"""
    logger.info("\n" + "=" * 70)
    logger.info("🚀 HANOI TRAVEL - FULL STACK STARTUP")
    logger.info("=" * 70 + "\n")

    try:
        # Step 1: Check Docker
        if not check_docker():
            logger.error("❌ Docker is not running. Please start Docker Desktop.")
            return 1

        # Step 2: Start databases (docker-compose - port 5433)
        # NOTE: Không cần start_auth_db_container() nữa
        # vì đã có unified database từ docker-compose
        if not start_docker_databases():
            return 1

        # Step 3: Start backend
        if not start_backend():
            return 1

        # Step 4: Start frontend
        if not start_frontend():
            logger.error("❌ Failed to start frontend")
            logger.info("\n💡 Backend is still running. Press CTRL+C to stop.")
            logger.info(f"   Or open {BACKEND_URL}/docs to test API")
            monitor_services()
            return 1

        # Step 5: Monitor services
        monitor_services()

    except KeyboardInterrupt:
        logger.info("\n👋 Interrupted by user")
    finally:
        cleanup()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
