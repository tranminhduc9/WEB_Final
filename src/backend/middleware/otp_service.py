"""
OTP Service Middleware

Module này xử lý OTP (One-Time Password) cho forgot/reset password
và các tính năng xác thực hai yếu tố.
"""

import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import hashlib
import os

logger = logging.getLogger(__name__)


class OTPConfig:
    """Cấu hình cho OTP service"""

    # OTP settings
    OTP_LENGTH = 6  # Số chữ số OTP
    OTP_EXPIRY = 10  # Thời gian hết hạn (phút)
    MAX_ATTEMPTS = 3  # Số lần thử tối đa
    COOLDOWN_PERIOD = 15  # Phút cooldown sau khi hết attempts

    # Redis key patterns
    OTP_KEY_PREFIX = "otp:"
    ATTEMPTS_KEY_PREFIX = "otp_attempts:"
    COOLDOWN_KEY_PREFIX = "otp_cooldown:"

    # Security settings
    USE_ENCRYPTION = True
    ENCRYPTION_KEY = os.getenv("OTP_ENCRYPTION_KEY", "default-key-change-in-production")


class OTPService:
    """
    Service xử lý OTP generation, validation và management

    Cung cấp các chức năng:
    - Tạo OTP ngẫu nhiên
    - Lưu OTP với expiry time
    - Validate OTP
    - Quản lý attempts và cooldown
    - Encryption cho security
    """

    def __init__(self, redis_client=None):
        """
        Khởi tạo OTP service

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.config = OTPConfig()

    def generate_otp(self, length: int = None) -> str:
        """
        Tạo OTP ngẫu nhiên

        Args:
            length: Độ dài OTP (mặc định từ config)

        Returns:
            str: OTP string
        """
        length = length or self.config.OTP_LENGTH
        return ''.join(random.choices(string.digits, k=length))

    def _encrypt_otp(self, otp: str) -> str:
        """
        Mã hóa OTP để lưu trữ

        Args:
            otp: OTP gốc

        Returns:
            str: OTP đã mã hóa
        """
        if not self.config.USE_ENCRYPTION:
            return otp

        try:
            # Enhanced encryption using SHA-256 with key and randomness
            key = self.config.ENCRYPTION_KEY.encode()
            # Use both timestamp and random uuid for uniqueness
            import uuid
            random_salt = str(uuid.uuid4())[:8]  # First 8 chars of UUID for randomness
            data = (otp + str(time.time()) + random_salt).encode()
            return hashlib.sha256(key + data).hexdigest()
        except Exception as e:
            logger.error(f"OTP encryption failed: {str(e)}")
            return otp

    async def create_otp(self, email: str, purpose: str = "password_reset") -> Dict[str, Any]:
        """
        Tạo và lưu OTP cho email

        Args:
            email: Email của user
            purpose: Mục đích sử dụng OTP

        Returns:
            Dict: OTP information
        """
        try:
            # Check cooldown
            if await self._is_in_cooldown(email):
                cooldown_remaining = await self._get_cooldown_remaining(email)
                raise Exception(f"Vui lòng đợi {cooldown_remaining} phút nữa để yêu cầu OTP mới")

            # Generate OTP
            otp = self.generate_otp()
            encrypted_otp = self._encrypt_otp(otp)
            expiry_time = datetime.utcnow() + timedelta(minutes=self.config.OTP_EXPIRY)

            # Save to Redis or memory
            if self.redis:
                await self._save_to_redis(email, encrypted_otp, expiry_time, purpose)
            else:
                await self._save_to_memory(email, encrypted_otp, expiry_time, purpose)

            # Reset attempts
            await self._reset_attempts(email)

            otp_info = {
                "otp": otp,  # Return plain OTP for email sending
                "email": email,
                "purpose": purpose,
                "expires_at": expiry_time.isoformat(),
                "expires_in_minutes": self.config.OTP_EXPIRY
            }

            logger.info(f"OTP generated for {email} - Purpose: {purpose}")
            return otp_info

        except Exception as e:
            logger.error(f"Failed to create OTP for {email}: {str(e)}")
            raise

    async def validate_otp(self, email: str, otp: str, purpose: str = "password_reset") -> bool:
        """
        Validate OTP

        Args:
            email: Email của user
            otp: OTP cần validate
            purpose: Mục đích sử dụng OTP

        Returns:
            bool: True nếu OTP hợp lệ
        """
        try:
            # Check cooldown
            if await self._is_in_cooldown(email):
                return False

            # Check attempts
            attempts = await self._get_attempts(email)
            if attempts >= self.config.MAX_ATTEMPTS:
                await self._set_cooldown(email)
                return False

            # Get stored OTP
            stored_otp = await self._get_stored_otp(email, purpose)
            if not stored_otp:
                await self._increment_attempts(email)
                return False

            # Check expiry
            if await self._is_otp_expired(email, purpose):
                await self._increment_attempts(email)
                return False

            # Validate OTP
            encrypted_otp = self._encrypt_otp(otp)
            if encrypted_otp == stored_otp:
                # Clear OTP after successful validation
                await self._clear_otp(email, purpose)
                await self._reset_attempts(email)
                logger.info(f"OTP validated successfully for {email}")
                return True
            else:
                await self._increment_attempts(email)
                logger.warning(f"Invalid OTP attempt for {email}")
                return False

        except Exception as e:
            logger.error(f"OTP validation error for {email}: {str(e)}")
            return False

    async def _save_to_redis(self, email: str, otp: str, expiry_time: datetime, purpose: str):
        """Lưu OTP vào Redis"""
        key = f"{self.config.OTP_KEY_PREFIX}{email}:{purpose}"
        ttl = int((expiry_time - datetime.utcnow()).total_seconds())
        await self.redis.setex(key, ttl, otp)

    async def _save_to_memory(self, email: str, otp: str, expiry_time: datetime, purpose: str):
        """Lưu OTP vào memory (fallback)"""
        # Simple memory storage - in production, use Redis
        if not hasattr(self, '_memory_storage'):
            self._memory_storage = {}

        key = f"{email}:{purpose}"
        self._memory_storage[key] = {
            "otp": otp,
            "expires_at": expiry_time
        }

    async def _get_stored_otp(self, email: str, purpose: str) -> Optional[str]:
        """Lấy OTP đã lưu"""
        if self.redis:
            key = f"{self.config.OTP_KEY_PREFIX}{email}:{purpose}"
            return await self.redis.get(key)
        else:
            if hasattr(self, '_memory_storage'):
                key = f"{email}:{purpose}"
                data = self._memory_storage.get(key)
                if data and datetime.utcnow() < data["expires_at"]:
                    return data["otp"]
            return None

    async def _is_otp_expired(self, email: str, purpose: str) -> bool:
        """Kiểm tra OTP có hết hạn không"""
        if self.redis:
            return not await self._get_stored_otp(email, purpose)
        else:
            if hasattr(self, '_memory_storage'):
                key = f"{email}:{purpose}"
                data = self._memory_storage.get(key)
                return not data or datetime.utcnow() >= data["expires_at"]
            return True

    async def _clear_otp(self, email: str, purpose: str):
        """Xóa OTP sau khi sử dụng"""
        if self.redis:
            key = f"{self.config.OTP_KEY_PREFIX}{email}:{purpose}"
            await self.redis.delete(key)
        else:
            if hasattr(self, '_memory_storage'):
                key = f"{email}:{purpose}"
                self._memory_storage.pop(key, None)

    async def _get_attempts(self, email: str) -> int:
        """Lấy số lần thử OTP"""
        if self.redis:
            key = f"{self.config.ATTEMPTS_KEY_PREFIX}{email}"
            attempts = await self.redis.get(key)
            return int(attempts) if attempts else 0
        else:
            return 0  # Simplified for memory fallback

    async def _increment_attempts(self, email: str):
        """Tăng số lần thử OTP"""
        if self.redis:
            key = f"{self.config.ATTEMPTS_KEY_PREFIX}{email}"
            await self.redis.incr(key)
            await self.redis.expire(key, self.config.COOLDOWN_PERIOD * 60)

    async def _reset_attempts(self, email: str):
        """Reset số lần thử OTP"""
        if self.redis:
            key = f"{self.config.ATTEMPTS_KEY_PREFIX}{email}"
            await self.redis.delete(key)

    async def _is_in_cooldown(self, email: str) -> bool:
        """Kiểm tra có trong cooldown không"""
        if self.redis:
            key = f"{self.config.COOLDOWN_KEY_PREFIX}{email}"
            return await self.redis.exists(key)
        return False

    async def _set_cooldown(self, email: str):
        """Set cooldown cho email"""
        if self.redis:
            key = f"{self.config.COOLDOWN_KEY_PREFIX}{email}"
            await self.redis.setex(key, self.config.COOLDOWN_PERIOD * 60, "1")

    async def _get_cooldown_remaining(self, email: str) -> int:
        """Lấy thời gian cooldown còn lại"""
        if self.redis:
            key = f"{self.config.COOLDOWN_KEY_PREFIX}{email}"
            ttl = await self.redis.ttl(key)
            return max(0, ttl // 60)
        return 0


# Global OTP service instance
otp_service = OTPService()


# Decorators
def require_otp(purpose: str = "password_reset"):
    """
    Decorator yêu cầu OTP validation

    Args:
        purpose: Mục đích sử dụng OTP
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            email = kwargs.get('email')
            otp = kwargs.get('otp')

            if not email or not otp:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": "Email và OTP là bắt buộc",
                        "data": None,
                        "error_code": "VALIDATE_001"
                    }
                )

            # Validate OTP
            is_valid = await otp_service.validate_otp(email, otp, purpose)
            if not is_valid:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "message": "OTP không hợp lệ hoặc đã hết hạn",
                        "data": None,
                        "error_code": "AUTH_003"
                    }
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Utility functions
def generate_secure_otp(length: int = 6) -> str:
    """
    Tạo OTP an toàn hơn

    Args:
        length: Độ dài OTP

    Returns:
        str: Secure OTP
    """
    # Sử dụng SystemRandom cho security cao hơn
    secure_random = random.SystemRandom()
    return ''.join(str(secure_random.randint(0, 9)) for _ in range(length))


def format_otp_for_display(otp: str) -> str:
    """
    Format OTP để hiển thị thân thiện

    Args:
        otp: OTP gốc

    Returns:
        str: OTP đã format
    """
    if len(otp) == 6:
        return f"{otp[:3]} {otp[3:]}"
    return otp


def is_valid_email_for_otp(email: str) -> bool:
    """
    Validate email cho OTP

    Args:
        email: Email cần kiểm tra

    Returns:
        bool: True nếu hợp lệ
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


async def cleanup_expired_otps():
    """
    Cleanup expired OTPs
    """
    # This function should be called periodically to clean up expired OTPs
    if hasattr(otp_service, '_memory_storage'):
        current_time = datetime.utcnow()
        expired_keys = []

        for key, data in otp_service._memory_storage.items():
            if isinstance(data, dict) and current_time >= data.get("expires_at", current_time):
                expired_keys.append(key)

        for key in expired_keys:
            del otp_service._memory_storage[key]

        logger.info(f"Cleaned up {len(expired_keys)} expired OTPs")