"""
Request Throttling Middleware

Module này cung cấp progressive throttling để chống brute force attacks.
Khi phát hiện nhiều request thất bại liên tiếp, delay sẽ tăng dần theo cấp số nhân.

Features:
- Progressive delay: 1s → 2s → 4s → 8s → 16s...
- Account lockout sau N lần thất bại
- Tự động reset sau thời gian timeout
- Memory-based với optional Redis support
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
import logging
import os
import hashlib

logger = logging.getLogger(__name__)


# ==============================================
# CONFIGURATION
# ==============================================

class ThrottleConfig:
    """Cấu hình throttling"""
    
    # Số lần thất bại tối đa trước khi lockout
    MAX_FAILED_ATTEMPTS = int(os.getenv("THROTTLE_MAX_ATTEMPTS", "5"))
    
    # Thời gian lockout (giây) - mặc định 15 phút
    LOCKOUT_DURATION = int(os.getenv("THROTTLE_LOCKOUT_DURATION", "900"))
    
    # Base delay (giây) - delay ban đầu
    BASE_DELAY = float(os.getenv("THROTTLE_BASE_DELAY", "1.0"))
    
    # Delay tối đa (giây)
    MAX_DELAY = float(os.getenv("THROTTLE_MAX_DELAY", "30.0"))
    
    # Multiplier cho exponential backoff
    DELAY_MULTIPLIER = float(os.getenv("THROTTLE_DELAY_MULTIPLIER", "2.0"))
    
    # Thời gian reset nếu không có attempt mới (giây) - mặc định 30 phút
    RESET_TIMEOUT = int(os.getenv("THROTTLE_RESET_TIMEOUT", "1800"))
    
    # Các endpoint được throttle
    THROTTLED_ENDPOINTS = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
    ]
    
    # Enable/Disable throttling
    ENABLED = os.getenv("THROTTLE_ENABLED", "true").lower() == "true"


# ==============================================
# THROTTLE TRACKER
# ==============================================

class ThrottleTracker:
    """
    Theo dõi và quản lý throttling cho từng identifier (IP hoặc email)
    
    Lưu trữ:
    - Số lần thất bại
    - Thời điểm thất bại cuối
    - Trạng thái lockout
    """
    
    def __init__(self):
        # Format: {identifier: {"attempts": int, "last_attempt": float, "locked_until": float}}
        self._data: Dict[str, Dict] = defaultdict(lambda: {
            "attempts": 0,
            "last_attempt": 0,
            "locked_until": 0
        })
        self._cleanup_interval = 300  # Cleanup mỗi 5 phút
        self._last_cleanup = time.time()
    
    def _get_key(self, identifier: str, endpoint: str = "") -> str:
        """Tạo key unique cho identifier + endpoint"""
        combined = f"{identifier}:{endpoint}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _cleanup_expired(self):
        """Dọn dẹp các entries đã hết hạn"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = []
        for key, data in self._data.items():
            # Reset nếu quá thời gian timeout
            if data["last_attempt"] > 0:
                if now - data["last_attempt"] > ThrottleConfig.RESET_TIMEOUT:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._data[key]
        
        self._last_cleanup = now
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired throttle entries")
    
    def record_attempt(self, identifier: str, endpoint: str = "", success: bool = False) -> None:
        """
        Ghi nhận một attempt
        
        Args:
            identifier: IP hoặc email
            endpoint: Endpoint được gọi
            success: True nếu thành công (reset counter)
        """
        self._cleanup_expired()
        key = self._get_key(identifier, endpoint)
        
        if success:
            # Reset khi thành công
            self._data[key] = {
                "attempts": 0,
                "last_attempt": 0,
                "locked_until": 0
            }
            logger.debug(f"Throttle reset for {identifier}")
        else:
            # Tăng counter khi thất bại
            self._data[key]["attempts"] += 1
            self._data[key]["last_attempt"] = time.time()
            
            # Lockout nếu vượt ngưỡng
            if self._data[key]["attempts"] >= ThrottleConfig.MAX_FAILED_ATTEMPTS:
                self._data[key]["locked_until"] = time.time() + ThrottleConfig.LOCKOUT_DURATION
                logger.warning(f"Account locked for {identifier} due to {self._data[key]['attempts']} failed attempts")
    
    def get_delay(self, identifier: str, endpoint: str = "") -> float:
        """
        Tính delay cần áp dụng dựa trên số lần thất bại
        
        Formula: delay = min(BASE_DELAY * (MULTIPLIER ^ attempts), MAX_DELAY)
        
        Args:
            identifier: IP hoặc email
            endpoint: Endpoint
            
        Returns:
            float: Số giây cần delay (0 nếu không cần)
        """
        key = self._get_key(identifier, endpoint)
        data = self._data.get(key)
        
        if not data or data["attempts"] == 0:
            return 0
        
        # Kiểm tra reset timeout
        if data["last_attempt"] > 0:
            if time.time() - data["last_attempt"] > ThrottleConfig.RESET_TIMEOUT:
                # Đã quá thời gian, reset
                self._data[key]["attempts"] = 0
                return 0
        
        # Tính delay theo exponential backoff
        delay = ThrottleConfig.BASE_DELAY * (ThrottleConfig.DELAY_MULTIPLIER ** (data["attempts"] - 1))
        return min(delay, ThrottleConfig.MAX_DELAY)
    
    def is_locked(self, identifier: str, endpoint: str = "") -> Tuple[bool, int]:
        """
        Kiểm tra xem identifier có bị lock không
        
        Args:
            identifier: IP hoặc email
            endpoint: Endpoint
            
        Returns:
            Tuple[bool, int]: (is_locked, remaining_seconds)
        """
        key = self._get_key(identifier, endpoint)
        data = self._data.get(key)
        
        if not data:
            return False, 0
        
        locked_until = data.get("locked_until", 0)
        if locked_until <= 0:
            return False, 0
        
        remaining = locked_until - time.time()
        if remaining <= 0:
            # Lock đã hết hạn
            self._data[key]["locked_until"] = 0
            return False, 0
        
        return True, int(remaining)
    
    def get_attempts(self, identifier: str, endpoint: str = "") -> int:
        """Lấy số lần attempt hiện tại"""
        key = self._get_key(identifier, endpoint)
        return self._data.get(key, {}).get("attempts", 0)
    
    def reset(self, identifier: str, endpoint: str = "") -> None:
        """Reset throttle cho identifier"""
        key = self._get_key(identifier, endpoint)
        if key in self._data:
            del self._data[key]
            logger.info(f"Manually reset throttle for {identifier}")


# Global tracker instance
throttle_tracker = ThrottleTracker()


# ==============================================
# THROTTLE MIDDLEWARE
# ==============================================

def get_client_identifier(request: Request) -> str:
    """
    Lấy identifier của client (ưu tiên IP)
    
    Xử lý cả trường hợp có proxy (X-Forwarded-For)
    """
    # Kiểm tra X-Forwarded-For header (khi có reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Lấy IP đầu tiên (client thực)
        return forwarded_for.split(",")[0].strip()
    
    # Kiểm tra X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to request client
    if request.client:
        return request.client.host
    
    return "unknown"


async def apply_throttle(request: Request, identifier: str = None, endpoint: str = None) -> None:
    """
    Áp dụng throttle delay nếu cần
    
    Args:
        request: FastAPI Request
        identifier: Custom identifier (mặc định dùng IP)
        endpoint: Custom endpoint (mặc định dùng request path)
        
    Raises:
        HTTPException: Nếu bị lockout
    """
    if not ThrottleConfig.ENABLED:
        return
    
    # Lấy identifier
    if identifier is None:
        identifier = get_client_identifier(request)
    
    # Lấy endpoint
    if endpoint is None:
        endpoint = request.url.path
    
    # Kiểm tra có phải endpoint cần throttle không
    should_throttle = False
    for throttled_endpoint in ThrottleConfig.THROTTLED_ENDPOINTS:
        if endpoint.startswith(throttled_endpoint):
            should_throttle = True
            break
    
    if not should_throttle:
        return
    
    # Kiểm tra lockout
    is_locked, remaining = throttle_tracker.is_locked(identifier, endpoint)
    if is_locked:
        logger.warning(f"Throttle: {identifier} is locked for {remaining}s on {endpoint}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "ACCOUNT_LOCKED",
                "message": f"Tài khoản tạm thời bị khóa. Vui lòng thử lại sau {remaining // 60} phút {remaining % 60} giây.",
                "retry_after": remaining
            },
            headers={"Retry-After": str(remaining)}
        )
    
    # Tính và áp dụng delay
    delay = throttle_tracker.get_delay(identifier, endpoint)
    if delay > 0:
        attempts = throttle_tracker.get_attempts(identifier, endpoint)
        logger.info(f"Throttle: Applying {delay:.1f}s delay for {identifier} (attempt #{attempts})")
        
        # Delay bất đồng bộ
        await asyncio.sleep(delay)


def record_failed_attempt(request: Request, identifier: str = None, endpoint: str = None) -> None:
    """
    Ghi nhận một attempt thất bại
    
    Gọi sau khi xác thực thất bại (wrong password, invalid token, etc.)
    """
    if not ThrottleConfig.ENABLED:
        return
    
    if identifier is None:
        identifier = get_client_identifier(request)
    
    if endpoint is None:
        endpoint = request.url.path
    
    throttle_tracker.record_attempt(identifier, endpoint, success=False)
    
    attempts = throttle_tracker.get_attempts(identifier, endpoint)
    remaining_attempts = ThrottleConfig.MAX_FAILED_ATTEMPTS - attempts
    
    if remaining_attempts > 0:
        logger.info(f"Throttle: Failed attempt #{attempts} for {identifier}. {remaining_attempts} attempts remaining.")
    else:
        logger.warning(f"Throttle: {identifier} has been locked out after {attempts} failed attempts.")


def record_successful_attempt(request: Request, identifier: str = None, endpoint: str = None) -> None:
    """
    Ghi nhận một attempt thành công (reset counter)
    
    Gọi sau khi xác thực thành công
    """
    if not ThrottleConfig.ENABLED:
        return
    
    if identifier is None:
        identifier = get_client_identifier(request)
    
    if endpoint is None:
        endpoint = request.url.path
    
    throttle_tracker.record_attempt(identifier, endpoint, success=True)


def get_throttle_status(request: Request, identifier: str = None, endpoint: str = None) -> Dict:
    """
    Lấy trạng thái throttle hiện tại
    
    Returns:
        Dict: {"attempts": int, "delay": float, "is_locked": bool, "remaining_lockout": int}
    """
    if identifier is None:
        identifier = get_client_identifier(request)
    
    if endpoint is None:
        endpoint = request.url.path
    
    attempts = throttle_tracker.get_attempts(identifier, endpoint)
    delay = throttle_tracker.get_delay(identifier, endpoint)
    is_locked, remaining = throttle_tracker.is_locked(identifier, endpoint)
    
    return {
        "attempts": attempts,
        "max_attempts": ThrottleConfig.MAX_FAILED_ATTEMPTS,
        "current_delay": delay,
        "is_locked": is_locked,
        "remaining_lockout": remaining
    }


# ==============================================
# ADMIN FUNCTIONS
# ==============================================

def admin_reset_throttle(identifier: str, endpoint: str = "") -> bool:
    """
    Admin function để reset throttle cho một identifier
    
    Args:
        identifier: IP hoặc email cần reset
        endpoint: Endpoint cụ thể (hoặc "" cho tất cả)
        
    Returns:
        bool: True nếu thành công
    """
    try:
        throttle_tracker.reset(identifier, endpoint)
        return True
    except Exception as e:
        logger.error(f"Failed to reset throttle for {identifier}: {e}")
        return False


def admin_get_all_throttled() -> Dict:
    """
    Admin function để lấy danh sách tất cả các entries đang bị throttle
    
    Returns:
        Dict: Tất cả throttle entries
    """
    result = {}
    for key, data in throttle_tracker._data.items():
        if data["attempts"] > 0:
            result[key] = {
                "attempts": data["attempts"],
                "last_attempt": datetime.fromtimestamp(data["last_attempt"]).isoformat() if data["last_attempt"] else None,
                "locked_until": datetime.fromtimestamp(data["locked_until"]).isoformat() if data["locked_until"] else None
            }
    return result


# Log configuration on startup
logger.info("Request Throttling Configuration:")
logger.info(f"  - Enabled: {ThrottleConfig.ENABLED}")
logger.info(f"  - Max attempts before lockout: {ThrottleConfig.MAX_FAILED_ATTEMPTS}")
logger.info(f"  - Lockout duration: {ThrottleConfig.LOCKOUT_DURATION}s ({ThrottleConfig.LOCKOUT_DURATION // 60} minutes)")
logger.info(f"  - Base delay: {ThrottleConfig.BASE_DELAY}s")
logger.info(f"  - Max delay: {ThrottleConfig.MAX_DELAY}s")
logger.info(f"  - Delay multiplier: {ThrottleConfig.DELAY_MULTIPLIER}x")
