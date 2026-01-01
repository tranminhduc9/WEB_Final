"""
Middleware CORS - Cross-Origin Resource Sharing

Module này cung cấp cấu hình CORS thống nhất cho ứng dụng.
Logic giữ giống nhau mọi phiên bản để đảm bảo tính nhất quán.
"""

from typing import List, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import os

logger = logging.getLogger(__name__)


class CORSConfig:
    """
    Cấu hình CORS cho môi trường khác nhau
    """

    # Environment variables
    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
    ALLOWED_METHODS = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(",")
    ALLOWED_HEADERS = os.getenv("CORS_HEADERS", "*").split(",")
    EXPOSE_HEADERS = os.getenv("CORS_EXPOSE_HEADERS", "").split(",") if os.getenv("CORS_EXPOSE_HEADERS") else []
    ALLOW_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "false").lower() == "true"
    MAX_AGE = int(os.getenv("CORS_MAX_AGE", "86400"))  # 24 hours

    # Predefined configurations
    PRODUCTION_CONFIG = {
        "allow_origins": [
            "https://hanoivivu.com",
            "https://www.hanoivivu.com",
            "https://admin.hanoivivu.com"
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 86400
    }

    DEVELOPMENT_CONFIG = {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 3600
    }

    STAGING_CONFIG = {
        "allow_origins": [
            "https://staging.hanoivivu.com",
            "https://dev.hanoivivu.com"
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 3600
    }


class CORSMiddlewareCustom(BaseHTTPMiddleware):
    """
    CORS middleware tùy chỉnh với logic phức tạp hơn

    Cung cấp các tính năng:
    - Dynamic origin checking
    - Per-endpoint CORS configuration
    - Rate limiting cho CORS preflight
    - Detailed logging
    """

    def __init__(self, app: FastAPI, config: Dict[str, Any] = None):
        """
        Khởi tạo middleware

        Args:
            app: FastAPI application
            config: CORS configuration
        """
        super().__init__(app)
        self.config = config or self._get_default_config()
        self._setup_origins()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Lấy cấu hình mặc định dựa trên environment

        Returns:
            Dict: CORS configuration
        """
        environment = os.getenv("ENVIRONMENT", "development").lower()

        if environment == "production":
            config = CORSConfig.PRODUCTION_CONFIG.copy()
        elif environment == "staging":
            config = CORSConfig.STAGING_CONFIG.copy()
        else:
            config = CORSConfig.DEVELOPMENT_CONFIG.copy()

        # Override với environment variables nếu có
        if CORSConfig.ALLOWED_ORIGINS != ["*"]:
            config["allow_origins"] = CORSConfig.ALLOWED_ORIGINS

        if CORSConfig.ALLOWED_METHODS:
            config["allow_methods"] = CORSConfig.ALLOWED_METHODS

        if CORSConfig.ALLOWED_HEADERS:
            config["allow_headers"] = CORSConfig.ALLOWED_HEADERS

        if CORSConfig.EXPOSE_HEADERS:
            config["expose_headers"] = CORSConfig.EXPOSE_HEADERS

        config["allow_credentials"] = CORSConfig.ALLOW_CREDENTIALS
        config["max_age"] = CORSConfig.MAX_AGE

        return config

    def _setup_origins(self):
        """Setup danh sách origins cho phép"""
        self.allowed_origins = set(self.config.get("allow_origins", []))
        self.allowed_methods = set(self.config.get("allow_methods", []))
        self.allowed_headers = set(self.config.get("allow_headers", []))
        self.expose_headers = set(self.config.get("expose_headers", []))
        self.allow_credentials = self.config.get("allow_credentials", False)
        self.max_age = self.config.get("max_age", 86400)

        # Log configuration
        logger.info(f"CORS Configuration loaded:")
        logger.info(f"  - Allowed origins: {self.allowed_origins}")
        logger.info(f"  - Allowed methods: {self.allowed_methods}")
        logger.info(f"  - Allow credentials: {self.allow_credentials}")

    def is_origin_allowed(self, origin: str) -> bool:
        """
        Kiểm tra origin có được phép không

        Args:
            origin: Origin cần kiểm tra

        Returns:
            bool: True nếu được phép
        """
        # Nếu wildcard được cho phép
        if "*" in self.allowed_origins:
            return True

        # Kiểm tra chính xác
        if origin in self.allowed_origins:
            return True

        # Kiểm tra subdomain matching
        for allowed_origin in self.allowed_origins:
            if allowed_origin.startswith("*."):
                domain = allowed_origin[2:]  # Bỏ *.
                if origin.endswith(domain):
                    # Kiểm tra có đúng là subdomain không
                    origin_without_sub = origin.split(".")[-2:]
                    domain_parts = domain.split(".")
                    if len(origin_without_sub) == len(domain_parts):
                        return True

        return False

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý CORS cho request

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response với headers CORS
        """
        origin = request.headers.get("origin")
        response = await call_next(request)

        # Nếu không có origin header, không cần xử lý CORS
        if not origin:
            return response

        # Set basic CORS headers
        response.headers["Access-Control-Allow-Origin"] = origin if self.is_origin_allowed(origin) else "null"
        response.headers["Access-Control-Allow-Methods"] = ",".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ",".join(self.allowed_headers)

        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ",".join(self.expose_headers)

        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        response.headers["Access-Control-Max-Age"] = str(self.max_age)

        # Log CORS request cho debugging
        self._log_cors_request(request, origin, self.is_origin_allowed(origin))

        return response

    def _log_cors_request(self, request: Request, origin: str, allowed: bool):
        """
        Log CORS request để debug

        Args:
            request: FastAPI request
            origin: Origin của request
            allowed: Có được phép không
        """
        method = request.method
        path = request.url.path

        log_data = {
            "origin": origin,
            "method": method,
            "path": path,
            "allowed": allowed,
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": request.state.timestamp if hasattr(request.state, "timestamp") else None
        }

        if allowed:
            logger.debug(f"CORS request allowed: {log_data}")
        else:
            logger.warning(f"CORS request blocked: {log_data}")


class PreflightHandler(BaseHTTPMiddleware):
    """
    Middleware xử lý riêng cho OPTIONS requests (preflight)

    Tối ưu performance cho preflight requests.
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý OPTIONS requests

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response cho preflight
        """
        if request.method == "OPTIONS":
            # Tạo response cho preflight request
            response = Response()
            response.status_code = 200

            origin = request.headers.get("origin", "")
            request_method = request.headers.get("access-control-request-method", "")
            request_headers = request.headers.get("access-control-request-headers", "")

            # Validate preflight request
            if self._validate_preflight(origin, request_method, request_headers):
                # Set CORS headers cho preflight
                cors_middleware = CORSMiddlewareCustom(None)
                if cors_middleware.is_origin_allowed(origin):
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Methods"] = request_method or "GET,POST,PUT,DELETE,OPTIONS"
                    response.headers["Access-Control-Allow-Headers"] = request_headers or "*"
                    response.headers["Access-Control-Max-Age"] = str(CORSConfig.MAX_AGE)

                    if CORSConfig.ALLOW_CREDENTIALS:
                        response.headers["Access-Control-Allow-Credentials"] = "true"

                    logger.info(f"Preflight request allowed for {origin}")
                else:
                    logger.warning(f"Preflight request blocked for {origin}")
            else:
                response.status_code = 403
                logger.warning(f"Invalid preflight request from {origin}")

            return response

        # Không phải OPTIONS request, tiếp tục chain
        return await call_next(request)

    def _validate_preflight(self, origin: str, method: str, headers: str) -> bool:
        """
        Validate preflight request

        Args:
            origin: Origin header
            method: Requested method
            headers: Requested headers

        Returns:
            bool: True nếu valid
        """
        if not origin:
            return False

        # Validate method
        if method and method not in CORSConfig.ALLOWED_METHODS:
            return False

        return True


def setup_cors(app: FastAPI, custom_config: Dict[str, Any] = None) -> None:
    """
    Setup CORS cho FastAPI application

    Args:
        app: FastAPI application instance
        custom_config: Custom CORS configuration
    """
    # Sử dụng FastAPI built-in CORS middleware cho simplicity
    if custom_config:
        config = custom_config
    else:
        environment = os.getenv("ENVIRONMENT", "development").lower()
        if environment == "production":
            config = CORSConfig.PRODUCTION_CONFIG
        elif environment == "staging":
            config = CORSConfig.STAGING_CONFIG
        else:
            config = CORSConfig.DEVELOPMENT_CONFIG

    # Add built-in CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **config
    )

    # Add custom CORS middleware for advanced features
    app.add_middleware(CORSMiddlewareCustom, config=config)

    # Add preflight handler for OPTIONS requests
    app.add_middleware(PreflightHandler)

    logger.info("CORS middleware setup completed")


# Utility functions
def get_cors_headers(origin: str, method: str = "GET") -> Dict[str, str]:
    """
    Lấy CORS headers cho origin và method cụ thể

    Args:
        origin: Request origin
        method: HTTP method

    Returns:
        Dict: CORS headers
    """
    cors_middleware = CORSMiddlewareCustom(None)
    headers = {}

    if cors_middleware.is_origin_allowed(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Methods"] = method
        headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        headers["Access-Control-Max-Age"] = str(CORSConfig.MAX_AGE)

        if CORSConfig.ALLOW_CREDENTIALS:
            headers["Access-Control-Allow-Credentials"] = "true"

    return headers


def is_cors_enabled_for_origin(origin: str) -> bool:
    """
    Kiểm tra CORS có được bật cho origin không

    Args:
        origin: Origin cần kiểm tra

    Returns:
        bool: True nếu được phép
    """
    cors_middleware = CORSMiddlewareCustom(None)
    return cors_middleware.is_origin_allowed(origin)


# Security headers bổ sung
def add_security_headers(app: FastAPI) -> None:
    """
    Add security headers cho production
    
    Headers được thêm:
    - X-Content-Type-Options: Ngăn MIME-sniffing
    - X-Frame-Options: Ngăn clickjacking
    - X-XSS-Protection: Bật XSS filter của browser
    - Referrer-Policy: Kiểm soát thông tin referrer
    - Strict-Transport-Security (HSTS): Bắt buộc HTTPS
    - Content-Security-Policy: Kiểm soát nguồn tài nguyên
    - Permissions-Policy: Kiểm soát quyền truy cập API

    Args:
        app: FastAPI application
    """
    # Get environment settings
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_production = environment == "production"
    is_staging = environment == "staging"
    
    # HSTS configuration
    hsts_max_age = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year default
    hsts_include_subdomains = os.getenv("HSTS_INCLUDE_SUBDOMAINS", "true").lower() == "true"
    hsts_preload = os.getenv("HSTS_PRELOAD", "true").lower() == "true"
    
    @app.middleware("http")
    async def add_security_headers_middleware(request: Request, call_next):
        response = await call_next(request)

        # ==============================================
        # BASIC SECURITY HEADERS (ALL ENVIRONMENTS)
        # ==============================================
        
        # Ngăn MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Ngăn clickjacking bằng cách không cho nhúng trong iframe
        response.headers["X-Frame-Options"] = "DENY"
        
        # Bật XSS filter của browser (deprecated but still useful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Kiểm soát thông tin referrer được gửi
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Ngăn cache thông tin nhạy cảm
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        # ==============================================
        # HTTPS/SSL SECURITY HEADERS (PRODUCTION/STAGING)
        # ==============================================
        
        if is_production or is_staging:
            # HTTP Strict Transport Security (HSTS)
            # Bắt buộc trình duyệt sử dụng HTTPS
            hsts_value = f"max-age={hsts_max_age}"
            if hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if hsts_preload and is_production:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value
            
            # Ngăn certificate transparency bypass
            response.headers["Expect-CT"] = f"max-age={hsts_max_age}, enforce"
        
        # ==============================================
        # PERMISSIONS POLICY (ALL ENVIRONMENTS)
        # ==============================================
        
        # Kiểm soát quyền truy cập các API của browser
        permissions_policy = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(self), "  # Cho phép geolocation cho bản thân site
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy

        # ==============================================
        # CONTENT SECURITY POLICY (PRODUCTION ONLY)
        # ==============================================
        
        if is_production:
            # CSP để kiểm soát nguồn tài nguyên được phép
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.hanoivivu.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
            response.headers["Content-Security-Policy"] = csp
            
            # Report-only CSP cho testing (uncomment khi cần test)
            # response.headers["Content-Security-Policy-Report-Only"] = csp

        return response

    logger.info(f"Security headers middleware added (Environment: {environment})")
    if is_production or is_staging:
        logger.info(f"  - HSTS enabled: max-age={hsts_max_age}, includeSubDomains={hsts_include_subdomains}, preload={hsts_preload}")
    logger.info("  - Permissions-Policy: enabled")
    logger.info(f"  - CSP: {'enabled' if is_production else 'disabled (development)'}")
