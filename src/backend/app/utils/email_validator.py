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
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"

    def _get_api_key(self) -> str:
        """Lấy API key từ tham số hoặc environment variable"""
        return self.api_key or os.getenv("HUNTER_IO_API_KEY", "")

    async def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Xác thực email sử dụng Hunter.io API
        
        STRICT MODE: Nếu API fails, sẽ reject email (không cho phép đăng ký)

        Args:
            email: Email cần xác thực

        Returns:
            Dict: Kết quả validation
            {
                "status": "valid" | "invalid" | "risky" | "unknown",
                "score": 0-100,
                "deliverable": bool,
                "data": {...}  # Dữ liệu đầy đủ từ Hunter.io
                "api_error": bool  # True nếu có lỗi API
            }
        """
        # Debug mode
        debug_mode = os.getenv("HUNTER_IO_DEBUG", "false").lower() == "true"
        
        # Kiểm tra API key
        api_key = self._get_api_key()
        if not api_key:
            logger.error("Hunter.io API key not configured. Email validation is REQUIRED.")
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": {},
                "message": "Email validation service unavailable - API key not configured",
                "api_error": True
            }

        # Basic format validation trước khi gọi API
        if not self._basic_email_check(email):
            logger.warning(f"Email format validation failed: {email}")
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": {},
                "message": "Invalid email format",
                "api_error": False
            }

        try:
            # Gọi Hunter.io Email Verifier API
            async with httpx.AsyncClient(timeout=10.0) as client:
                if debug_mode:
                    logger.info(f"Calling Hunter.io API for email: {email}")
                
                response = await client.get(
                    f"{self.base_url}/email-verifier",
                    params={
                        "email": email,
                        "api_key": api_key
                    }
                )
                
                if debug_mode:
                    logger.info(f"Hunter.io API Response Status: {response.status_code}")
                    logger.info(f"Hunter.io API Response Body: {response.text[:500]}")

                # Xử lý response
                if response.status_code == 200:
                    data = response.json()
                    result = self._parse_hunter_response(data)
                    result["api_error"] = False
                    return result
                    
                elif response.status_code == 401:
                    logger.error("Hunter.io: Invalid API key - BLOCKING registration")
                    return {
                        "status": EmailStatus.INVALID,
                        "score": 0,
                        "deliverable": False,
                        "data": {},
                        "message": "Email validation service error - Invalid API credentials",
                        "api_error": True
                    }
                    
                elif response.status_code == 429:
                    logger.error("Hunter.io: Rate limit exceeded - BLOCKING registration")
                    return {
                        "status": EmailStatus.INVALID,
                        "score": 0,
                        "deliverable": False,
                        "data": {},
                        "message": "Email validation service temporarily unavailable - Rate limit exceeded",
                        "api_error": True
                    }
                    
                else:
                    logger.error(f"Hunter.io API error: {response.status_code} - BLOCKING registration")
                    return {
                        "status": EmailStatus.INVALID,
                        "score": 0,
                        "deliverable": False,
                        "data": {},
                        "message": f"Email validation service error - API returned status {response.status_code}",
                        "api_error": True
                    }

        except httpx.TimeoutException:
            logger.error("Hunter.io: Request timeout - BLOCKING registration")
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": {},
                "message": "Email validation service timeout - Please try again later",
                "api_error": True
            }
        except Exception as e:
            logger.error(f"Hunter.io validation error: {str(e)} - BLOCKING registration")
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": {},
                "message": f"Email validation service error - {str(e)}",
                "api_error": True
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
            # Debug mode
            debug_mode = os.getenv("HUNTER_IO_DEBUG", "false").lower() == "true"
            
            if debug_mode:
                logger.info(f"Parsing Hunter.io response: {data}")
            
            email_data = data.get("data", {})
            status_str = email_data.get("status", "unknown")
            score = email_data.get("score", 0)
            result_str = email_data.get("result", "unknown")
            
            # Map Hunter.io status sang EmailStatus enum
            status_mapping = {
                "valid": EmailStatus.VALID,
                "invalid": EmailStatus.INVALID,
                "risky": EmailStatus.RISKY,
                "unknown": EmailStatus.UNKNOWN,
                "accept_all": EmailStatus.RISKY,  # Accept-all servers are risky
                "webmail": EmailStatus.VALID  # Webmail is usually valid
            }
            
            status = status_mapping.get(status_str.lower(), EmailStatus.UNKNOWN)
            
            # Kiểm tra deliverable - linh hoạt hơn
            # Hunter.io API v2 có thể dùng "result" hoặc "deliverable" field
            # result can be: "deliverable", "undeliverable", "risky", "unknown", "accept_all"
            
            # Cách 1: Check result field
            deliverable = False
            if result_str in ["deliverable", "valid"]:
                deliverable = True
            elif result_str == "accept_all":
                # Accept-all servers - risky nhưng có thể deliverable
                deliverable = True if score >= 50 else False
            
            # Cách 2: Fallback check status field
            if not deliverable and status_str in ["valid", "webmail"]:
                deliverable = True
            
            # Cách 3: Check explicit deliverable field (nếu có)
            if "deliverable" in email_data:
                deliverable = email_data["deliverable"]
            
            # Additional info
            result = {
                "status": status,
                "score": score,
                "deliverable": deliverable,
                "data": {
                    "status": status_str,
                    "score": score,
                    "result": result_str,
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
            
            logger.info(f"Email validation result for {email_data.get('email', 'unknown')}: status={status_str}, score={score}, result={result_str}, deliverable={deliverable}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error parsing Hunter.io response: {str(e)}")
            logger.error(f"Response data: {data}")
            return {
                "status": EmailStatus.INVALID,
                "score": 0,
                "deliverable": False,
                "data": data,
                "message": f"Parse error: {str(e)}",
                "api_error": True
            }

    async def is_email_acceptable(self, email: str, min_score: int = 50) -> tuple[bool, str]:
        """
        Kiểm tra email có chấp nhận được để đăng ký không
        
        STRICT MODE: Chỉ chấp nhận email khi:
        - Hunter.io API hoạt động bình thường
        - Email được xác nhận là valid hoặc risky với score đủ cao

        Args:
            email: Email cần kiểm tra
            min_score: Score tối thiểu (default: 50)

        Returns:
            tuple: (is_acceptable: bool, message: str)
        """
        result = await self.validate_email(email)

        # Nếu có lỗi API - REJECT
        if result.get("api_error", False):
            error_msg = result.get("message", "Email validation service unavailable")
            logger.error(f"Email validation failed for {email}: {error_msg}")
            return False, error_msg

        # Email không hợp lệ về format - REJECT
        if result["status"] == EmailStatus.INVALID:
            return False, result.get("message", "Email is invalid or not deliverable")

        # Email hợp lệ và deliverable - ACCEPT
        if result["status"] == EmailStatus.VALID and result["deliverable"]:
            return True, "Email is valid and deliverable"

        # Email có rủi ro nhưng score đủ cao - ACCEPT
        if result["status"] == EmailStatus.RISKY and result["score"] >= min_score:
            return True, f"Email is acceptable (score: {result['score']})"

        # Email risky nhưng score quá thấp - REJECT
        if result["status"] == EmailStatus.RISKY:
            return False, f"Email score too low: {result['score']} (minimum: {min_score})"

        # Unknown status (không nên xảy ra với strict mode) - REJECT
        return False, "Could not verify email. Please try again later"


# Global instance
hunter_validator = HunterIOValidator()


# ==================== UTILITY FUNCTIONS ====================

async def validate_user_email(email: str, min_score: int = 50) -> tuple[bool, str, Dict[str, Any]]:
    """
    Hàm tiện ích để validate email cho user registration
    
    CHỈ GỌI Hunter.io API 1 LẦN và reuse kết quả.

    Args:
        email: Email cần validate
        min_score: Score tối thiểu

    Returns:
        tuple: (is_valid: bool, message: str, validation_data: dict)
    """
    # Gọi API 1 lần duy nhất
    result = await hunter_validator.validate_email(email)
    
    # Kiểm tra acceptability dựa trên kết quả đã có (không gọi API lại)
    # Nếu có lỗi API - REJECT
    if result.get("api_error", False):
        error_msg = result.get("message", "Email validation service unavailable")
        logger.error(f"Email validation failed for {email}: {error_msg}")
        return False, error_msg, result

    # Email không hợp lệ về format - REJECT
    if result["status"] == EmailStatus.INVALID:
        return False, result.get("message", "Email is invalid or not deliverable"), result

    # Email hợp lệ và deliverable - ACCEPT
    if result["status"] == EmailStatus.VALID and result["deliverable"]:
        return True, "Email is valid and deliverable", result

    # Email có rủi ro nhưng score đủ cao - ACCEPT
    if result["status"] == EmailStatus.RISKY and result["score"] >= min_score:
        return True, f"Email is acceptable (score: {result['score']})", result

    # Email risky nhưng score quá thấp - REJECT
    if result["status"] == EmailStatus.RISKY:
        return False, f"Email score too low: {result['score']} (minimum: {min_score})", result

    # Unknown status - REJECT
    return False, "Could not verify email. Please try again later", result

