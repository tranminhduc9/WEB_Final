"""
Secure Cookie Configuration Module

Module này cung cấp cấu hình và utilities cho việc quản lý cookies an toàn.
Đảm bảo cookies được bảo vệ khỏi các tấn công phổ biến như XSS, CSRF, session hijacking.

Security Features:
- Secure flag: Cookie chỉ gửi qua HTTPS
- HttpOnly flag: Ngăn JavaScript truy cập cookie
- SameSite flag: Ngăn CSRF attacks
- Domain/Path restrictions: Giới hạn scope của cookie
- Expiration management: Kiểm soát thời gian sống cookie
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.utils.timezone_helper import utc_now
from fastapi import Response, Request
from starlette.responses import JSONResponse
import secrets
import hashlib
import hmac
import base64
import json
import logging
import os

logger = logging.getLogger(__name__)


# ==============================================
# ENVIRONMENT CONFIGURATION
# ==============================================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
IS_STAGING = ENVIRONMENT == "staging"

# Session Secret - PHẢI THAY ĐỔI TRONG PRODUCTION
SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "dev-session-secret-change-in-production-immediately"
)

# Cảnh báo nếu sử dụng default secret trong production/staging
if (IS_PRODUCTION or IS_STAGING) and "dev-" in SESSION_SECRET:
    logger.warning("=" * 60)
    logger.warning("⚠️  CẢNH BÁO BẢO MẬT: Đang sử dụng SESSION_SECRET mặc định!")
    logger.warning("    Vui lòng tạo secret mới bằng: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    logger.warning("=" * 60)


# ==============================================
# COOKIE SECURITY CONFIGURATION
# ==============================================

class CookieConfig:
    """Cấu hình bảo mật cho cookies"""
    
    # Secure flag - chỉ gửi cookie qua HTTPS
    # True trong production/staging, False trong development
    SECURE: bool = IS_PRODUCTION or IS_STAGING
    
    # HttpOnly flag - ngăn JavaScript truy cập cookie
    # Luôn True để ngăn XSS attacks
    HTTP_ONLY: bool = True
    
    # SameSite flag - ngăn CSRF attacks
    # "strict": Cookie chỉ gửi khi same-site request
    # "lax": Cookie gửi cho top-level navigation
    # "none": Cookie gửi mọi request (yêu cầu Secure=True)
    SAME_SITE: str = os.getenv("COOKIE_SAME_SITE", "lax")
    
    # Domain - giới hạn domain nhận cookie
    # None = chỉ domain hiện tại
    DOMAIN: Optional[str] = os.getenv("COOKIE_DOMAIN", None)
    
    # Path - giới hạn path nhận cookie
    PATH: str = os.getenv("COOKIE_PATH", "/")
    
    # Max Age mặc định (giây)
    # Access token cookie: 1 giờ
    ACCESS_TOKEN_MAX_AGE: int = int(os.getenv("COOKIE_ACCESS_MAX_AGE", "3600"))
    
    # Refresh token cookie: 7 ngày
    REFRESH_TOKEN_MAX_AGE: int = int(os.getenv("COOKIE_REFRESH_MAX_AGE", "604800"))
    
    # Session cookie: 24 giờ
    SESSION_MAX_AGE: int = int(os.getenv("COOKIE_SESSION_MAX_AGE", "86400"))
    
    # Cookie names
    ACCESS_TOKEN_NAME: str = "access_token"
    REFRESH_TOKEN_NAME: str = "refresh_token"
    SESSION_ID_NAME: str = "session_id"
    CSRF_TOKEN_NAME: str = "csrf_token"
    
    @classmethod
    def get_cookie_settings(cls, cookie_type: str = "session") -> Dict[str, Any]:
        """
        Lấy cấu hình cookie dựa trên loại
        
        Args:
            cookie_type: "access", "refresh", "session", "csrf"
            
        Returns:
            Dict: Cookie settings
        """
        max_age_map = {
            "access": cls.ACCESS_TOKEN_MAX_AGE,
            "refresh": cls.REFRESH_TOKEN_MAX_AGE,
            "session": cls.SESSION_MAX_AGE,
            "csrf": cls.SESSION_MAX_AGE,
        }
        
        return {
            "secure": cls.SECURE,
            "httponly": cls.HTTP_ONLY if cookie_type != "csrf" else False,  # CSRF token needs JS access
            "samesite": cls.SAME_SITE,
            "domain": cls.DOMAIN,
            "path": cls.PATH,
            "max_age": max_age_map.get(cookie_type, cls.SESSION_MAX_AGE),
        }


# ==============================================
# SECURE COOKIE UTILITIES
# ==============================================

def generate_secure_token(length: int = 32) -> str:
    """
    Tạo token ngẫu nhiên an toàn
    
    Args:
        length: Độ dài token (bytes)
        
    Returns:
        str: URL-safe token
    """
    return secrets.token_urlsafe(length)


def generate_session_id() -> str:
    """
    Tạo Session ID an toàn
    
    Returns:
        str: Session ID duy nhất
    """
    # Kết hợp random bytes với timestamp để đảm bảo tính duy nhất
    random_bytes = secrets.token_bytes(24)
    timestamp = utc_now().timestamp()
    
    # Hash để tạo session ID
    data = f"{random_bytes.hex()}{timestamp}".encode()
    session_id = hashlib.sha256(data).hexdigest()[:48]
    
    return session_id


def sign_cookie_value(value: str, secret: str = None) -> str:
    """
    Ký giá trị cookie để ngăn tampering
    
    Args:
        value: Giá trị cần ký
        secret: Secret key (mặc định dùng SESSION_SECRET)
        
    Returns:
        str: Signed value format: value.signature
    """
    secret = secret or SESSION_SECRET
    signature = hmac.new(
        secret.encode(),
        value.encode(),
        hashlib.sha256
    ).hexdigest()[:32]
    
    return f"{value}.{signature}"


def verify_signed_cookie(signed_value: str, secret: str = None) -> Optional[str]:
    """
    Xác thực và lấy giá trị từ signed cookie
    
    Args:
        signed_value: Giá trị đã ký
        secret: Secret key
        
    Returns:
        str: Giá trị gốc nếu hợp lệ, None nếu không hợp lệ
    """
    if not signed_value or "." not in signed_value:
        return None
    
    try:
        value, signature = signed_value.rsplit(".", 1)
        expected = sign_cookie_value(value, secret)
        
        if hmac.compare_digest(signed_value, expected):
            return value
        return None
    except Exception as e:
        logger.warning(f"Cookie verification failed: {e}")
        return None


def generate_csrf_token() -> str:
    """
    Tạo CSRF token
    
    Returns:
        str: CSRF token
    """
    return generate_secure_token(32)


# ==============================================
# RESPONSE HELPERS
# ==============================================

def set_secure_cookie(
    response: Response,
    name: str,
    value: str,
    cookie_type: str = "session",
    sign: bool = True,
    **kwargs
) -> None:
    """
    Set cookie với cấu hình bảo mật
    
    Args:
        response: FastAPI/Starlette Response
        name: Tên cookie
        value: Giá trị cookie
        cookie_type: Loại cookie ("access", "refresh", "session", "csrf")
        sign: Có ký giá trị cookie không
        **kwargs: Override cookie settings
    """
    settings = CookieConfig.get_cookie_settings(cookie_type)
    settings.update(kwargs)
    
    # Ký giá trị nếu cần
    final_value = sign_cookie_value(value) if sign else value
    
    response.set_cookie(
        key=name,
        value=final_value,
        max_age=settings["max_age"],
        path=settings["path"],
        domain=settings["domain"],
        secure=settings["secure"],
        httponly=settings["httponly"],
        samesite=settings["samesite"],
    )
    
    logger.debug(f"Set secure cookie: {name} (type={cookie_type}, secure={settings['secure']})")


def delete_secure_cookie(response: Response, name: str) -> None:
    """
    Xóa cookie một cách an toàn
    
    Args:
        response: FastAPI/Starlette Response
        name: Tên cookie cần xóa
    """
    response.delete_cookie(
        key=name,
        path=CookieConfig.PATH,
        domain=CookieConfig.DOMAIN,
        secure=CookieConfig.SECURE,
        httponly=CookieConfig.HTTP_ONLY,
        samesite=CookieConfig.SAME_SITE,
    )
    logger.debug(f"Deleted cookie: {name}")


def get_cookie_value(request: Request, name: str, verify: bool = True) -> Optional[str]:
    """
    Lấy và xác thực giá trị cookie
    
    Args:
        request: FastAPI Request
        name: Tên cookie
        verify: Xác thực chữ ký
        
    Returns:
        str: Giá trị cookie hoặc None
    """
    cookie_value = request.cookies.get(name)
    
    if not cookie_value:
        return None
    
    if verify:
        return verify_signed_cookie(cookie_value)
    
    return cookie_value


# ==============================================
# AUTH COOKIE HELPERS
# ==============================================

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str = None
) -> None:
    """
    Set authentication cookies
    
    Args:
        response: FastAPI Response
        access_token: JWT access token
        refresh_token: JWT refresh token (optional)
    """
    # Set access token cookie
    set_secure_cookie(
        response,
        CookieConfig.ACCESS_TOKEN_NAME,
        access_token,
        cookie_type="access",
        sign=False  # JWT đã có chữ ký riêng
    )
    
    # Set refresh token cookie nếu có
    if refresh_token:
        set_secure_cookie(
            response,
            CookieConfig.REFRESH_TOKEN_NAME,
            refresh_token,
            cookie_type="refresh",
            sign=False  # JWT đã có chữ ký riêng
        )
    
    # Set CSRF token
    csrf_token = generate_csrf_token()
    set_secure_cookie(
        response,
        CookieConfig.CSRF_TOKEN_NAME,
        csrf_token,
        cookie_type="csrf",
        sign=True
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Xóa tất cả authentication cookies (logout)
    
    Args:
        response: FastAPI Response
    """
    delete_secure_cookie(response, CookieConfig.ACCESS_TOKEN_NAME)
    delete_secure_cookie(response, CookieConfig.REFRESH_TOKEN_NAME)
    delete_secure_cookie(response, CookieConfig.SESSION_ID_NAME)
    delete_secure_cookie(response, CookieConfig.CSRF_TOKEN_NAME)
    
    logger.info("Cleared all auth cookies")


# ==============================================
# SESSION MANAGEMENT
# ==============================================

class SecureSession:
    """
    Quản lý session an toàn
    
    Lưu trữ session data được mã hóa và ký trong cookie.
    """
    
    def __init__(self, request: Request):
        self.request = request
        self._data: Dict[str, Any] = {}
        self._session_id: Optional[str] = None
        self._modified: bool = False
        self._load()
    
    def _load(self):
        """Load session từ cookie"""
        session_cookie = get_cookie_value(
            self.request,
            CookieConfig.SESSION_ID_NAME,
            verify=True
        )
        
        if session_cookie:
            self._session_id = session_cookie
        else:
            self._session_id = generate_session_id()
            self._modified = True
    
    @property
    def session_id(self) -> str:
        """Get session ID"""
        return self._session_id
    
    def save(self, response: Response):
        """Lưu session vào response cookie"""
        if self._modified or self._session_id:
            set_secure_cookie(
                response,
                CookieConfig.SESSION_ID_NAME,
                self._session_id,
                cookie_type="session"
            )
    
    def destroy(self, response: Response):
        """Hủy session"""
        delete_secure_cookie(response, CookieConfig.SESSION_ID_NAME)
        self._session_id = None
        self._data = {}


# ==============================================
# CSRF PROTECTION
# ==============================================

def validate_csrf_token(request: Request, header_name: str = "X-CSRF-Token") -> bool:
    """
    Xác thực CSRF token
    
    So sánh token trong header với token trong cookie.
    
    Args:
        request: FastAPI Request
        header_name: Tên header chứa CSRF token
        
    Returns:
        bool: True nếu hợp lệ
    """
    # Lấy token từ cookie
    cookie_token = get_cookie_value(
        request,
        CookieConfig.CSRF_TOKEN_NAME,
        verify=True
    )
    
    if not cookie_token:
        logger.warning("CSRF cookie not found")
        return False
    
    # Lấy token từ header
    header_token = request.headers.get(header_name)
    
    if not header_token:
        logger.warning("CSRF header not found")
        return False
    
    # So sánh an toàn
    return hmac.compare_digest(cookie_token, header_token)


# Log cấu hình khi khởi động
logger.info("Cookie Security Configuration:")
logger.info(f"  - Environment: {ENVIRONMENT}")
logger.info(f"  - Secure: {CookieConfig.SECURE}")
logger.info(f"  - HttpOnly: {CookieConfig.HTTP_ONLY}")
logger.info(f"  - SameSite: {CookieConfig.SAME_SITE}")
logger.info(f"  - Session Secret: {'[SECURE]' if 'dev-' not in SESSION_SECRET else '[DEFAULT - INSECURE]'}")
