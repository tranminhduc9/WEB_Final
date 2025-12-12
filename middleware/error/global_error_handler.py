"""
Global Error Handler Middleware v2.0 cho WEB Final API

Triển khai centralized error handling với response format chuẩn:
- Catches all errors từ routes/controllers
- Consistent error response format theo API contract v1
- Custom error codes với tiếng Việt messages
- Support cho different error types (Auth, Validation, Database, etc.)
- Production-safe error responses (hide sensitive info)
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime

import pymongo.errors
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Safe import with fallback
try:
    from ..auth.jwt_middleware import AuthException
    from ..auth.rbac_middleware import RoleException
    from ..security.rate_limiter import RateLimitException
    from ..validation.validator import ValidationException
except ImportError:
    # Fallback for standalone usage
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from auth.jwt_middleware import AuthException
        from auth.rbac_middleware import RoleException
        from security.rate_limiter import RateLimitException
        from validation.validator import ValidationException
    except ImportError:
        # Define placeholder exceptions if modules not available
        class AuthException(Exception): pass
        class RoleException(Exception): pass
        class RateLimitException(Exception): pass
        class ValidationException(Exception): pass


logger = logging.getLogger(__name__)


class GlobalErrorHandler:
    """
    Global Error Handler for FastAPI applications.

    Handles all types of errors with consistent response format and proper logging.
    """

    def __init__(self, debug: bool = False, log_errors: bool = True):
        """
        Initialize Global Error Handler.

        Args:
            debug: Enable debug mode with detailed error information
            log_errors: Enable error logging
        """
        self.debug = debug
        self.log_errors = log_errors

    def format_error_response(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Union[list, dict]] = None,
        field: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format consistent error response theo API contract v1

        Args:
            error_code: Machine-readable error code
            message: Human-readable error message (tiếng Việt)
            status_code: HTTP status code
            details: Additional error details (cho validation errors)
            field: Field name cho field-specific errors
            request_id: Request ID cho tracking

        Returns:
            Formatted error response dictionary theo chuẩn API
        """
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
        }

        # Add optional fields
        if details:
            response["data"] = details
        else:
            response["data"] = None

        # Add pagination field (empty cho errors)
        response["pagination"] = None

        # Add debug information trong development mode
        if self.debug:
            response["debug"] = {
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "field": field,
            }

        return response

    async def handle_http_exception(
        self,
        request: Request,
        exc: HTTPException
    ) -> JSONResponse:
        """
        Handle standard HTTP exceptions với Vietnamese messages

        Args:
            request: FastAPI request object
            exc: HTTPException instance

        Returns:
            JSONResponse with formatted error theo API v1
        """
        # Error code và message mapping theo status code
        error_mappings = {
            status.HTTP_400_BAD_REQUEST: {
                "code": "HTTP_400",
                "message": "Yêu cầu không hợp lệ"
            },
            status.HTTP_401_UNAUTHORIZED: {
                "code": "HTTP_401",
                "message": "Yêu cầu xác thực (Unauthorized)"
            },
            status.HTTP_403_FORBIDDEN: {
                "code": "HTTP_403",
                "message": "Bạn không có quyền truy cập (Forbidden)"
            },
            status.HTTP_404_NOT_FOUND: {
                "code": "HTTP_404",
                "message": "Tài nguyên không tìm thấy (Not Found)"
            },
            status.HTTP_405_METHOD_NOT_ALLOWED: {
                "code": "HTTP_405",
                "message": "Phương thức không được hỗ trợ (Method Not Allowed)"
            },
            status.HTTP_409_CONFLICT: {
                "code": "HTTP_409",
                "message": "Xung đột dữ liệu (Conflict)"
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "code": "HTTP_422",
                "message": "Dữ liệu không thể xử lý (Unprocessable Entity)"
            },
            status.HTTP_429_TOO_MANY_REQUESTS: {
                "code": "HTTP_429",
                "message": "Vượt quá giới hạn yêu cầu (Too Many Requests)"
            },
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "code": "HTTP_500",
                "message": "Lỗi server nội bộ (Internal Server Error)"
            },
            status.HTTP_502_BAD_GATEWAY: {
                "code": "HTTP_502",
                "message": "Lỗi Gateway (Bad Gateway)"
            },
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "code": "HTTP_503",
                "message": "Dịch vụ không khả dụng (Service Unavailable)"
            },
            status.HTTP_504_GATEWAY_TIMEOUT: {
                "code": "HTTP_504",
                "message": "Gateway Timeout"
            },
        }

        error_info = error_mappings.get(exc.status_code, {
            "code": "HTTP_ERROR",
            "message": "Lỗi HTTP không xác định"
        })

        # Log HTTP errors
        if self.log_errors:
            logger.warning(
                f"HTTP {exc.status_code} error cho {request.method} {request.url.path}: {str(exc.detail)}"
            )

        # Extract custom message từ exception nếu có
        message = error_info["message"]
        if isinstance(exc.detail, dict) and "message" in exc.detail:
            message = exc.detail["message"]
        elif isinstance(exc.detail, str) and exc.status_code not in [401, 403, 404]:
            # Use custom message cho non-auth errors
            message = str(exc.detail)

        # Handle custom error codes từ middleware của chúng ta
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict) and 'error_code' in exc.detail:
            error_info["code"] = exc.detail['error_code']
            message = exc.detail.get('message', message)

        return JSONResponse(
            status_code=exc.status_code,
            content=self.format_error_response(
                error_code=error_info["code"],
                message=message,
                status_code=exc.status_code,
                details=exc.detail if isinstance(exc.detail, list) else None
            )
        )

    async def handle_validation_error(
        self,
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle RequestValidationError với Vietnamese messages

        Args:
            request: FastAPI request object
            exc: RequestValidationError instance

        Returns:
            JSONResponse với formatted validation error theo API v1
        """
        # Format validation errors
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])

            # Translate Pydantic error messages sang tiếng Việt
            vietnamese_message = self._translate_validation_error(error)

            details.append({
                "field": field,
                "message": vietnamese_message,
                "value": error.get("input"),
                "type": error["type"]
            })

        # Log validation errors
        if self.log_errors:
            logger.warning(
                f"Validation error cho {request.method} {request.url.path}: "
                f"{len(details)} validation errors"
            )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=self.format_error_response(
                error_code="VALIDATION_ERROR",
                message="Dữ liệu không hợp lệ. Vui lòng kiểm tra lại các trường thông tin.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details
            )
        )

    def _translate_validation_error(self, error: Dict[str, Any]) -> str:
        """
        Translate Pydantic validation error sang tiếng Việt
        """
        error_type = error.get("type", "")
        field = ".".join(str(loc) for loc in error.get("loc", []))

        # Common Vietnamese error messages
        translations = {
            "value_error.missing": f"Thiếu trường bắt buộc: {field}",
            "value_error.not_in": f"Giá trị không hợp lệ cho trường {field}",
            "value_error.email": "Email không hợp lệ",
            "value_error.url": "URL không hợp lệ",
            "value_error.str.regex": f"Định dạng không hợp lệ cho trường {field}",
            "value_error.number.not_ge": f"Giá trị của {field} phải lớn hơn hoặc bằng {error.get('ctx', {}).get('ge_value', 0)}",
            "value_error.number.not_le": f"Giá trị của {field} phải nhỏ hơn hoặc bằng {error.get('ctx', {}).get('le_value', 0)}",
            "value_error.number.not_gt": f"Giá trị của {field} phải lớn hơn {error.get('ctx', {}).get('gt_value', 0)}",
            "value_error.number.not_lt": f"Giá trị của {field} phải nhỏ hơn {error.get('ctx', {}).get('lt_value', 0)}",
            "value_error.length.missing": f"Thiếu giá trị cho trường {field}",
            "value_error.str.length": f"Độ dài của trường {field} không hợp lệ",
            "value_error.any_str.min_length": f"Trường {field} phải có ít nhất {error.get('ctx', {}).get('min_length', 1)} ký tự",
            "value_error.any_str.max_length": f"Trường {field} không được vượt quá {error.get('ctx', {}).get('max_length', 255)} ký tự",
        }

        return translations.get(error_type, error.get("msg", f"Lỗi validation tại trường {field}"))

    async def handle_pydantic_validation_error(
        self,
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic ValidationError.

        Args:
            request: FastAPI request object
            exc: ValidationError instance

        Returns:
            JSONResponse with formatted validation error
        """
        # Format validation errors
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            details.append({
                "field": field,
                "message": error["msg"],
                "value": error.get("input"),
                "type": error["type"]
            })

        # Log validation errors
        if self.log_errors:
            logger.warning(
                f"Pydantic validation error for {request.method} {request.url.path}: "
                f"{len(details)} validation errors"
            )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=self.format_error_response(
                error_code="VALIDATION_ERROR",
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details
            )
        )

    async def handle_mongo_errors(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle MongoDB-specific errors.

        Args:
            request: FastAPI request object
            exc: MongoDB exception instance

        Returns:
            JSONResponse with formatted error
        """
        # Handle duplicate key error (code 11000)
        if isinstance(exc, pymongo.errors.DuplicateKeyError):
            # Extract duplicate field from error message
            duplicate_field = "unknown"
            if "index:" in str(exc):
                # Try to extract field name from error
                error_str = str(exc)
                if "_id_" in error_str:
                    duplicate_field = "id"
                elif "email" in error_str.lower():
                    duplicate_field = "email"
                elif "username" in error_str.lower():
                    duplicate_field = "username"

            if self.log_errors:
                logger.warning(
                    f"Duplicate key error for {request.method} {request.url.path}: "
                    f"field={duplicate_field}"
                )

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=self.format_error_response(
                    error_code="DUPLICATE_ERROR",
                    message=f"Trùng lặp dữ liệu: {duplicate_field} đã tồn tại",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    field=duplicate_field
                )
            )

        # Handle other MongoDB errors
        if isinstance(exc, pymongo.errors.PyMongoError):
            if self.log_errors:
                logger.error(
                    f"MongoDB error for {request.method} {request.url.path}: {str(exc)}"
                )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=self.format_error_response(
                    error_code="DATABASE_ERROR",
                    message="Lỗi cơ sở dữ liệu",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            )

        # Not a MongoDB error, let it be handled by other handlers
        raise exc

    async def handle_auth_errors(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle authentication-related errors.

        Args:
            request: FastAPI request object
            exc: Authentication exception

        Returns:
            JSONResponse with formatted error
        """
        # Handle custom auth exceptions
        if isinstance(exc, (AuthException, RoleException, RateLimitException, ValidationException)):
            if self.log_errors:
                logger.warning(
                    f"Auth error for {request.method} {request.url.path}: "
                    f"{type(exc).__name__}: {str(exc)}"
                )

            # Extract error details from our custom exceptions
            status_code = exc.status_code if hasattr(exc, 'status_code') else status.HTTP_401_UNAUTHORIZED
            error_detail = exc.detail if hasattr(exc, 'detail') else str(exc)

            # Handle both dict and string error details
            if isinstance(error_detail, dict):
                error_code = error_detail.get("error", {}).get("code", "AUTH_ERROR")
                message = error_detail.get("error", {}).get("message", "Lỗi xác thực")
                details = error_detail.get("error", {}).get("details")
            else:
                error_code = "AUTH_ERROR"
                message = str(error_detail)
                details = None

            return JSONResponse(
                status_code=status_code,
                content=self.format_error_response(
                    error_code=error_code,
                    message=message,
                    status_code=status_code,
                    details=details
                )
            )

        # Handle JWT errors
        import jwt
        if isinstance(exc, (jwt.ExpiredSignatureError, jwt.InvalidTokenError)):
            if self.log_errors:
                logger.warning(
                    f"JWT error for {request.method} {request.url.path}: {type(exc).__name__}"
                )

            error_code = "TOKEN_EXPIRED" if isinstance(exc, jwt.ExpiredSignatureError) else "INVALID_TOKEN"
            message = "Token đã hết hạn" if isinstance(exc, jwt.ExpiredSignatureError) else "Token không hợp lệ"

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=self.format_error_response(
                    error_code=error_code,
                    message=message,
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            )

        # Not an auth error, let it be handled by other handlers
        raise exc

    async def handle_general_error(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle unexpected errors với production-safe responses

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse với formatted error theo API v1
        """
        if self.log_errors:
            logger.error(
                f"Lỗi không mong đợi cho {request.method} {request.url.path}: "
                f"{type(exc).__name__}: {str(exc)}",
                exc_info=True
            )

        # Không expose internal error details trong production
        if self.debug:
            message = f"Lỗi server nội bộ: {str(exc)}"
            details = {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        else:
            message = "Đã xảy ra lỗi server nội bộ. Vui lòng thử lại sau."
            details = None

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self.format_error_response(
                error_code="INTERNAL_SERVER_ERROR",
                message=message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=details
            )
        )


# Factory function for creating error handler
def create_global_error_handler(debug: bool = False, log_errors: bool = True) -> GlobalErrorHandler:
    """
    Create GlobalErrorHandler instance.

    Args:
        debug: Enable debug mode with detailed error information
        log_errors: Enable error logging

    Returns:
        GlobalErrorHandler instance
    """
    return GlobalErrorHandler(debug=debug, log_errors=log_errors)


# Global exception handler function
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for FastAPI applications.

    This function can be used as a FastAPI exception handler.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with formatted error
    """
    error_handler = GlobalErrorHandler(debug=False)  # Use env variable in real app

    try:
        # Route exceptions to appropriate handlers
        if isinstance(exc, HTTPException):
            return await error_handler.handle_http_exception(request, exc)
        elif isinstance(exc, RequestValidationError):
            return await error_handler.handle_validation_error(request, exc)
        elif isinstance(exc, ValidationError):
            return await error_handler.handle_pydantic_validation_error(request, exc)
        else:
            # Try to handle specific error types
            try:
                return await error_handler.handle_mongo_errors(request, exc)
            except:
                pass

            try:
                return await error_handler.handle_auth_errors(request, exc)
            except:
                pass

            # Fall back to general error handler
            return await error_handler.handle_general_error(request, exc)

    except Exception as handler_exc:
        # Last resort - if even the error handler fails
        logger.critical(f"Error handler failed: {str(handler_exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "CRITICAL_ERROR",
                    "message": "Lỗi hệ thống nghiêm trọng"
                }
            }
        )


# Usage examples:
#
# # Add exception handlers to FastAPI app
# app.add_exception_handler(Exception, global_exception_handler)
# app.add_exception_handler(RequestValidationError, global_exception_handler)
#
# # Create custom error handler
# error_handler = create_global_error_handler(debug=True)
# error_response = error_handler.format_error_response(
#     error_code="CUSTOM_ERROR",
#     message="Custom error message",
#     status_code=400
# )