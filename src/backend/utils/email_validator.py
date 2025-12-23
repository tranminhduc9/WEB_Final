"""
Hunter.io Email Validator

Module này cung cấp chức năng xác thực email sử dụng Hunter.io API
để kiểm tra xem email có hợp lệ và deliverable hay không.
"""

import httpx
import logging
import os
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class EmailStatus(Enum):
    """Enum cho trạng thái email"""
    VALID = "valid"           # Email hợp lệ và deliverable
    INVALID = "invalid"       # Email không hợp lệ
    RISKY = "risky"           # Email có rủi ro
    UNKNOWN = "unknown"       # Không thể xác định


class HunterIOValidator:
    """
    Class xác thực email sử dụng Hunter.io API

    Hunter.io cung cấp email verification API để kiểm tra:
    - Format email có đúng không
    - Domain có tồn tại không
    - Email có deliverable không
    """

    def __init__(self, api_key: str = None):
        """
        Khởi tạo Hunter.io validator

        Args:
            api_key: Hunter.io API key (lấy từ environment nếu không cung cấp)
        """
        self.api_key = api_key or os.getenv("HUNTER_IO_API_KEY")
        self.base_url = "https://api.hunter.io/v2"

        if not self.api_key:
            logger.warning("Hunter.io API key not found. Email validation will be disabled.")

    async def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Xác thực email sử dụng Hunter.io API

        Args:
            email: Email cần xác thực

        Returns:
            Dict: Kết quả validation
            {
                "status": "valid" | "invalid" | "risky" | "unknown",
                "score": 0-100,
                "deliverable": bool,
                "data": {...}  # Dữ liệu đầy đủ từ Hunter.io
            }
        """
        # Kiểm tra API key
        if not self.api_key:
            logger.warning("Hunter.io API key not configured. Skipping validation.")
            return {
                "status": EmailStatus.UNKNOWN,
                "score": 0,
                "deliverable": None,
                "data": {},
                "message": "Email validation disabled"
            }

        # Basic format validation trước khi gọi API
        if not self._basic_email_check(email):
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": {},
                "message": "Invalid email format"
            }

        try:
            # Gọi Hunter.io Email Verifier API
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/email-verifier",
                    params={
                        "email": email,
                        "api_key": self.api_key
                    }
                )

                # Xử lý response
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_hunter_response(data)
                elif response.status_code == 401:
                    logger.error("Hunter.io: Invalid API key")
                    return {
                        "status": EmailStatus.UNKNOWN,
                        "score": 0,
                        "deliverable": None,
                        "data": {},
                        "message": "Invalid API key"
                    }
                elif response.status_code == 429:
                    logger.warning("Hunter.io: Rate limit exceeded")
                    return {
                        "status": EmailStatus.UNKNOWN,
                        "score": 0,
                        "deliverable": None,
                        "data": {},
                        "message": "Rate limit exceeded"
                    }
                else:
                    logger.error(f"Hunter.io API error: {response.status_code}")
                    return {
                        "status": EmailStatus.UNKNOWN,
                        "score": 0,
                        "deliverable": None,
                        "data": {},
                        "message": f"API error: {response.status_code}"
                    }

        except httpx.TimeoutException:
            logger.error("Hunter.io: Request timeout")
            return {
                "status": EmailStatus.UNKNOWN,
                "score": 0,
                "deliverable": None,
                "data": {},
                "message": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Hunter.io validation error: {str(e)}")
            return {
                "status": EmailStatus.UNKNOWN,
                "score": 0,
                "deliverable": None,
                "data": {},
                "message": f"Validation error: {str(e)}"
            }

    def _basic_email_check(self, email: str) -> bool:
        """
        Basic email format check (regex)

        Args:
            email: Email cần kiểm tra

        Returns:
            bool: True nếu format đúng
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+(?<!\.)\.[a-zA-Z]{2,}$'

        # Check consecutive dots
        if '..' in email:
            return False

        return bool(re.match(pattern, email))

    def _parse_hunter_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response từ Hunter.io API

        Args:
            data: Response data từ Hunter.io

        Returns:
            Dict: Parsed validation result
        """
        try:
            email_data = data.get("data", {})
            status_str = email_data.get("status", "unknown")
            score = email_data.get("score", 0)

            # Map Hunter.io status sang EmailStatus enum
            status_mapping = {
                "valid": EmailStatus.VALID,
                "invalid": EmailStatus.INVALID,
                "risky": EmailStatus.RISKY,
                "unknown": EmailStatus.UNKNOWN
            }

            status = status_mapping.get(status_str, EmailStatus.UNKNOWN)

            # Kiểm tra deliverable
            deliverable = email_data.get("deliverable", False)

            # Additional info
            result = {
                "status": status,
                "score": score,
                "deliverable": deliverable,
                "data": {
                    "status": status_str,
                    "score": score,
                    "deliverable": deliverable,
                    "domain": email_data.get("domain", {}),
                    "mailbox": email_data.get("mailbox", ""),
                    "reason": email_data.get("reason", ""),
                    "free_email": email_data.get("free_email", False),
                    "disposable": email_data.get("disposable", False),
                    "webmail": email_data.get("webmail", False)
                },
                "message": f"Email is {status_str}"
            }

            logger.info(f"Email validation result for {email_data.get('email', 'unknown')}: {status_str} (score: {score})")

            return result

        except Exception as e:
            logger.error(f"Error parsing Hunter.io response: {str(e)}")
            return {
                "status": EmailStatus.UNKNOWN,
                "score": 0,
                "deliverable": None,
                "data": data,
                "message": f"Parse error: {str(e)}"
            }

    async def is_email_acceptable(self, email: str, min_score: int = 50) -> tuple[bool, str]:
        """
        Kiểm tra email có chấp nhận được để đăng ký không

        Args:
            email: Email cần kiểm tra
            min_score: Score tối thiểu (default: 50)

        Returns:
            tuple: (is_acceptable: bool, message: str)
        """
        result = await self.validate_email(email)

        # Nếu validation disabled (no API key)
        if result["status"] == EmailStatus.UNKNOWN and result.get("message") == "Email validation disabled":
            return True, "Email validation disabled, proceeding with registration"

        # Email hợp lệ
        if result["status"] == EmailStatus.VALID and result["deliverable"]:
            return True, "Email is valid and deliverable"

        # Email có rủi ro nhưng score đủ cao
        if result["status"] == EmailStatus.RISKY and result["score"] >= min_score:
            return True, f"Email is acceptable (score: {result['score']})"

        # Email không hợp lệ
        if result["status"] == EmailStatus.INVALID:
            return False, "Email is invalid or not deliverable"

        # Email risky nhưng score quá thấp
        if result["status"] == EmailStatus.RISKY:
            return False, f"Email score too low: {result['score']} (minimum: {min_score})"

        # Unknown status
        return False, "Could not verify email. Please try again later"


# Global instance
hunter_validator = HunterIOValidator()


# ==================== UTILITY FUNCTIONS ====================

async def validate_user_email(email: str, min_score: int = 50) -> tuple[bool, str, Dict[str, Any]]:
    """
    Hàm tiện ích để validate email cho user registration

    Args:
        email: Email cần validate
        min_score: Score tối thiểu

    Returns:
        tuple: (is_valid: bool, message: str, validation_data: dict)
    """
    result = await hunter_validator.validate_email(email)
    is_acceptable, message = await hunter_validator.is_email_acceptable(email, min_score)

    return is_acceptable, message, result
