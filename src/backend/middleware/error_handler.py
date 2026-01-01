"""
Middleware Error Handling - Xử lý lỗi thống nhất

Module này cung cấp xử lý lỗi tập trung cho toàn bộ ứng dụng,
đảm bảo format response lỗi nhất quán và thông tin đầy đủ.
Chuẩn hóa lỗi cho tất cả các phiên bản.
"""

import traceback
import uuid
from datetime import datetime
from app.utils.timezone_helper import utc_now
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
import os

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """
    Mã lỗi chuẩn hóa cho ứng dụng

    Mỗi loại lỗi có một mã định danh duy nhất để dễ dàng
    theo dõi và xử lý ở frontend.
    """
    # Authentication errors (1000-1099)
    INVALID_CREDENTIALS = "AUTH_1001"
    TOKEN_EXPIRED = "AUTH_1002"
    TOKEN_INVALID = "AUTH_1003"
    INSUFFICIENT_PERMISSIONS = "AUTH_1004"
    USER_NOT_FOUND = "AUTH_1005"
    USER_ALREADY_EXISTS = "AUTH_1006"
    PASSWORD_TOO_WEAK = "AUTH_1007"
    EMAIL_NOT_VERIFIED = "AUTH_1008"

    # Validation errors (2000-2099)
    INVALID_INPUT = "VALID_2001"
    MISSING_REQUIRED_FIELD = "VALID_2002"
    INVALID_EMAIL_FORMAT = "VALID_2003"
    INVALID_PASSWORD_FORMAT = "VALID_2004"
    FILE_TOO_LARGE = "VALID_2005"
    INVALID_FILE_TYPE = "VALID_2006"

    # Business logic errors (3000-3099)
    RESOURCE_NOT_FOUND = "BIZ_3001"
    RESOURCE_ALREADY_EXISTS = "BIZ_3002"
    OPERATION_NOT_ALLOWED = "BIZ_3003"
    QUOTA_EXCEEDED = "BIZ_3004"
    DUPLICATE_ACTION = "BIZ_3005"

    # System errors (5000-5099)
    DATABASE_ERROR = "SYS_5001"
    EXTERNAL_SERVICE_ERROR = "SYS_5002"
    RATE_LIMIT_EXCEEDED = "SYS_5003"
    INTERNAL_SERVER_ERROR = "SYS_5004"
    SERVICE_UNAVAILABLE = "SYS_5005"

    # File upload errors (6000-6099)
    UPLOAD_FAILED = "FILE_6001"
    INVALID_IMAGE_FORMAT = "FILE_6002"
    IMAGE_PROCESSING_ERROR = "FILE_6003"


class ErrorCategory(Enum):
    """Phân loại lỗi theo mức độ nghiêm trọng"""
    CLIENT_ERROR = "client_error"  # 4xx - Lỗi từ client
    SERVER_ERROR = "server_error"  # 5xx - Lỗi từ server
    BUSINESS_ERROR = "business_error"  # Logic error
    VALIDATION_ERROR = "validation_error"  # Validation error


class APIError(Exception):
    """
    Custom error class cho API errors

    Cung cấp structured error information cho responses.
    """

    def __init__(
        self,
        message: str,
        error_code: str = ErrorCode.INTERNAL_SERVER_ERROR.value,
        status_code: int = 500,
        category: ErrorCategory = ErrorCategory.SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """
        Khởi tạo API error

        Args:
            message: Message chi tiết cho developer
            error_code: Mã lỗi chuẩn hóa
            status_code: HTTP status code
            category: Phân loại lỗi
            details: Chi tiết bổ sung
            user_message: Message thân thiện cho user
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.category = category
        self.details = details or {}
        self.user_message = user_message or self._get_default_user_message()

    def _get_default_user_message(self) -> str:
        """Lấy message mặc định cho user dựa trên error_code"""
        if self.error_code.startswith("AUTH_"):
            return "Lỗi xác thực. Vui lòng đăng nhập lại."
        elif self.error_code.startswith("VALID_"):
            return "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại."
        elif self.error_code.startswith("BIZ_"):
            return "Thao tác không hợp lệ. Vui lòng thử lại."
        elif self.error_code.startswith("SYS_"):
            return "Hệ thống đang gặp sự cố. Vui lòng thử lại sau."
        elif self.error_code.startswith("FILE_"):
            return "Lỗi xử lý file. Vui lòng thử lại."
        else:
            return "Đã xảy ra lỗi. Vui lòng thử lại."

    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi thành dictionary cho API response

        Returns:
            Dict: Error response structure
        """
        return {
            "success": False,
            "error_code": self.error_code,
            "message": self.user_message,
            "details": self.details if os.getenv("DEBUG", "false").lower() == "true" else {},
            "timestamp": utc_now().isoformat(),
            "category": self.category.value
        }


class ValidationError(APIError):
    """Validation error chuyên biệt"""

    def __init__(
        self,
        message: str,
        field: str = None,
        invalid_value: Any = None,
        user_message: str = None
    ):
        details = {}
        if field:
            details["field"] = field
        if invalid_value is not None:
            details["invalid_value"] = str(invalid_value)

        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT.value,
            status_code=400,
            category=ErrorCategory.VALIDATION_ERROR,
            details=details,
            user_message=user_message
        )


class AuthenticationError(APIError):
    """Authentication error chuyên biệt"""

    def __init__(self, message: str, user_message: str = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS.value,
            status_code=401,
            category=ErrorCategory.CLIENT_ERROR,
            user_message=user_message
        )


class AuthorizationError(APIError):
    """Authorization error chuyên biệt"""

    def __init__(self, message: str, user_message: str = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS.value,
            status_code=403,
            category=ErrorCategory.CLIENT_ERROR,
            user_message=user_message or "Bạn không có quyền thực hiện hành động này."
        )


class NotFoundError(APIError):
    """Resource not found error chuyên biệt"""

    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" with ID: {resource_id}"

        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_NOT_FOUND.value,
            status_code=404,
            category=ErrorCategory.CLIENT_ERROR,
            user_message=f"Không tìm thấy {resource_type.lower()}."
        )


class ConflictError(APIError):
    """Conflict error chuyên biệt"""

    def __init__(self, message: str, user_message: str = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS.value,
            status_code=409,
            category=ErrorCategory.BUSINESS_ERROR,
            user_message=user_message
        )


class RateLimitError(APIError):
    """Rate limit error chuyên biệt"""

    def __init__(self, retry_after: int = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message="Rate limit exceeded",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED.value,
            status_code=429,
            category=ErrorCategory.CLIENT_ERROR,
            details=details,
            user_message="Bạn đã thực hiện quá nhiều yêu cầu. Vui lòng thử lại sau."
        )


class ErrorHandler:
    """
    Centralized error handler

    Xử lý và chuyển đổi các loại exception khác nhau thành APIError.
    """

    def __init__(self):
        """Khởi tạo error handler"""
        self.error_mappings = self._setup_error_mappings()

    def _setup_error_mappings(self) -> Dict[type, callable]:
        """
        Setup mapping cho các exception types

        Returns:
            Dict: Mapping từ exception type sang handler function
        """
        return {
            HTTPException: self._handle_http_exception,
            StarletteHTTPException: self._handle_http_exception,
            ValidationError: self._handle_validation_error,
            ValueError: self._handle_value_error,
            PermissionError: self._handle_permission_error,
            FileNotFoundError: self._handle_not_found_error,
            ConnectionError: self._handle_connection_error,
            TimeoutError: self._handle_timeout_error,
        }

    def handle_exception(self, exception: Exception) -> APIError:
        """
        Handle và convert exception thành APIError

        Args:
            exception: Exception cần xử lý

        Returns:
            APIError: API error đã được chuẩn hóa
        """
        exception_type = type(exception)

        # Check direct mappings
        if exception_type in self.error_mappings:
            return self.error_mappings[exception_type](exception)

        # Check if it's already an APIError
        if isinstance(exception, APIError):
            return exception

        # Default handling
        return self._handle_unknown_exception(exception)

    def _handle_http_exception(self, exception: HTTPException) -> APIError:
        """Handle HTTP exceptions"""
        # Map status code sang appropriate error
        if exception.status_code == 401:
            return AuthenticationError(str(exception.detail))
        elif exception.status_code == 403:
            return AuthorizationError(str(exception.detail))
        elif exception.status_code == 404:
            return NotFoundError("Resource")
        elif exception.status_code == 422:
            return ValidationError(
                message="Validation failed",
                user_message=str(exception.detail)
            )
        else:
            return APIError(
                message=str(exception.detail),
                status_code=exception.status_code,
                category=ErrorCategory.CLIENT_ERROR
            )

    def _handle_validation_error(self, exception: ValidationError) -> APIError:
        """Handle Pydantic validation errors"""
        errors = exception.errors()
        field_errors = []

        for error in errors:
            field_path = " -> ".join(str(loc) for loc in error.get("loc", []))
            field_errors.append({
                "field": field_path,
                "message": error.get("msg", "Invalid value"),
                "value": error.get("input")
            })

        return APIError(
            message=f"Validation failed: {str(errors)}",
            error_code=ErrorCode.INVALID_INPUT.value,
            status_code=422,
            category=ErrorCategory.VALIDATION_ERROR,
            details={"field_errors": field_errors},
            user_message="Dữ liệu không hợp lệ. Vui lòng kiểm tra lại các trường đã nhập."
        )

    def _handle_value_error(self, exception: ValueError) -> APIError:
        """Handle value errors"""
        return ValidationError(
            message=str(exception),
            user_message="Giá trị không hợp lệ. Vui lòng kiểm tra lại."
        )

    def _handle_permission_error(self, exception: PermissionError) -> APIError:
        """Handle permission errors"""
        return AuthorizationError(str(exception))

    def _handle_not_found_error(self, exception: FileNotFoundError) -> APIError:
        """Handle file not found errors"""
        return NotFoundError("File")

    def _handle_connection_error(self, exception: ConnectionError) -> APIError:
        """Handle connection errors"""
        return APIError(
            message=f"Connection error: {str(exception)}",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR.value,
            status_code=503,
            category=ErrorCategory.SERVER_ERROR,
            user_message="Không thể kết nối đến dịch vụ bên ngoài. Vui lòng thử lại sau."
        )

    def _handle_timeout_error(self, exception: TimeoutError) -> APIError:
        """Handle timeout errors"""
        return APIError(
            message=f"Timeout error: {str(exception)}",
            error_code=ErrorCode.SERVICE_UNAVAILABLE.value,
            status_code=504,
            category=ErrorCategory.SERVER_ERROR,
            user_message="Yêu cầu xử lý quá lâu. Vui lòng thử lại."
        )

    def _handle_unknown_exception(self, exception: Exception) -> APIError:
        """Handle unknown exceptions"""
        error_id = str(uuid.uuid4())

        # Log full error for debugging
        logger.error(f"Unhandled exception [{error_id}]: {str(exception)}", exc_info=True)

        return APIError(
            message=f"Unexpected error: {str(exception)}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            status_code=500,
            category=ErrorCategory.SERVER_ERROR,
            details={
                "error_id": error_id,
                "exception_type": type(exception).__name__
            },
            user_message="Đã xảy ra lỗi không mong muốn. Vui lòng thử lại hoặc liên hệ hỗ trợ."
        )


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware để xử lý errors tập trung

    Tự động bắt và xử lý tất cả exceptions trong requests.
    """

    def __init__(self, app):
        """
        Khởi tạo middleware

        Args:
            app: FastAPI application
        """
        super().__init__(app)
        self.error_handler = ErrorHandler()

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và bắt exceptions

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response với error handling
        """
        try:
            response = await call_next(request)
            return response

        except Exception as exception:
            # Convert exception thành APIError
            api_error = self.error_handler.handle_exception(exception)

            # Log error
            self._log_error(api_error, request, exception)

            # Return JSON response
            return self._create_error_response(api_error)

    def _log_error(self, api_error: APIError, request: Request, original_exception: Exception):
        """
        Log error cho monitoring

        Args:
            api_error: API error object
            request: FastAPI request
            original_exception: Original exception
        """
        log_data = {
            "error_code": api_error.error_code,
            "status_code": api_error.status_code,
            "message": api_error.message,
            "url": str(request.url) if request else None,
            "method": request.method if request else None,
            "user_agent": request.headers.get("User-Agent") if request else None,
            "client_ip": self._get_client_ip(request) if request else None
        }

        if api_error.category == ErrorCategory.SERVER_ERROR:
            logger.error(f"Server Error: {log_data}", exc_info=original_exception)
        elif api_error.category == ErrorCategory.CLIENT_ERROR:
            logger.warning(f"Client Error: {log_data}")
        else:
            logger.info(f"Application Error: {log_data}")

    def _get_client_ip(self, request: Request) -> str:
        """Lấy client IP từ request"""
        if not request:
            return "unknown"

        # Check various headers
        headers = ["X-Forwarded-For", "X-Real-IP", "X-Client-IP"]
        for header in headers:
            ip = request.headers.get(header)
            if ip:
                return ip.split(",")[0].strip()

        return request.client.host if request.client else "unknown"

    def _create_error_response(self, api_error: APIError) -> JSONResponse:
        """
        Tạo error response JSON

        Args:
            api_error: API error object

        Returns:
            JSONResponse: Error response
        """
        response_data = api_error.to_dict()

        # Add request ID nếu có
        response_data["request_id"] = getattr(
            getattr(api_error, 'request', None),
            'state',
            {}
        ).get('request_id')

        return JSONResponse(
            status_code=api_error.status_code,
            content=response_data
        )


# Global error handler instance
error_handler = ErrorHandler()


# Decorator cho error handling
def handle_errors(func):
    """
    Decorator để tự động handle errors trong functions

    Args:
        func: Function cần decorate
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            api_error = error_handler.handle_exception(e)
            raise HTTPException(
                status_code=api_error.status_code,
                detail=api_error.to_dict()
            )

    return wrapper


# Utility functions
def create_error_response(
    message: str,
    error_code: str = ErrorCode.INTERNAL_SERVER_ERROR.value,
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Tạo error response structure

    Args:
        message: Error message
        error_code: Error code
        status_code: HTTP status code
        details: Additional details

    Returns:
        Dict: Error response
    """
    api_error = APIError(
        message=message,
        error_code=error_code,
        status_code=status_code,
        details=details
    )

    return api_error.to_dict()


def get_error_message_by_code(error_code: str) -> str:
    """
    Lấy user-friendly message bằng error code

    Args:
        error_code: Error code

    Returns:
        str: User-friendly message
    """
    error_messages = {
        ErrorCode.INVALID_CREDENTIALS.value: "Email hoặc mật khẩu không chính xác.",
        ErrorCode.TOKEN_EXPIRED.value: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        ErrorCode.TOKEN_INVALID.value: "Token không hợp lệ. Vui lòng đăng nhập lại.",
        ErrorCode.RESOURCE_NOT_FOUND.value: "Không tìm thấy tài nguyên.",
        ErrorCode.RESOURCE_ALREADY_EXISTS.value: "Tài nguyên đã tồn tại.",
        ErrorCode.INVALID_INPUT.value: "Dữ liệu đầu vào không hợp lệ.",
        ErrorCode.RATE_LIMIT_EXCEEDED.value: "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
        ErrorCode.INTERNAL_SERVER_ERROR.value: "Lỗi hệ thống. Vui lòng thử lại sau.",
    }

    return error_messages.get(error_code, "Đã xảy ra lỗi. Vui lòng thử lại.")


def is_client_error(error_code: str) -> bool:
    """
    Kiểm tra có phải client error không

    Args:
        error_code: Error code

    Returns:
        bool: True nếu là client error
    """
    return error_code.startswith(("AUTH_", "VALID_", "BIZ_"))


def is_server_error(error_code: str) -> bool:
    """
    Kiểm tra có phải server error không

    Args:
        error_code: Error code

    Returns:
        bool: True nếu là server error
    """
    return error_code.startswith(("SYS_", "FILE_"))