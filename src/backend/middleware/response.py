"""
Response Standardization Middleware

Module này cung cấp utilities để tạo response theo format chuẩn
của hệ thống API, đảm bảo consistency cho tất cả endpoints.
"""

from typing import Any, Optional, Dict, List
from fastapi import Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """
    Class chuẩn hóa API response format

    Format chuẩn:
    {
      "success": true/false,
      "message": "Mô tả ngắn gọn",
      "data": {...},  // hoặc []
      "pagination": {...}, // optional
      "error_code": "..."  // optional
    }
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Thao tác thành công",
        status_code: int = 200,
        pagination: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Tạo success response

        Args:
            data: Dữ liệu cần trả về
            message: Message mô tả
            status_code: HTTP status code
            pagination: Pagination info

        Returns:
            JSONResponse: Standardized success response
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }

        # Add pagination nếu có
        if pagination:
            response_data["pagination"] = pagination

        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    @staticmethod
    def error(
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Tạo error response

        Args:
            message: Error message
            error_code: Error code cho debugging
            status_code: HTTP status code
            details: Additional error details

        Returns:
            JSONResponse: Standardized error response
        """
        response_data = {
            "success": False,
            "message": message,
            "data": None
        }

        # Add error code nếu có
        if error_code:
            response_data["error_code"] = error_code

        # Add details nếu có (chỉ trong debug mode)
        import os
        if details and os.getenv("DEBUG", "false").lower() == "true":
            response_data["details"] = details

        return JSONResponse(
            content=response_data,
            status_code=status_code
        )

    @staticmethod
    def paginated(
        items: List[Any],
        current_page: int,
        total_items: int,
        limit: int,
        message: str = "Lấy dữ liệu thành công"
    ) -> JSONResponse:
        """
        Tạo paginated response

        Args:
            items: Danh sách items
            current_page: Trang hiện tại
            total_items: Tổng số items
            limit: Số items per page
            message: Message mô tả

        Returns:
            JSONResponse: Paginated response
        """
        total_pages = (total_items + limit - 1) // limit  # Ceiling division

        pagination = {
            "current_page": current_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "limit": limit
        }

        return APIResponse.success(
            data=items,
            message=message,
            pagination=pagination
        )

    @staticmethod
    def created(
        data: Any = None,
        message: str = "Tạo mới thành công"
    ) -> JSONResponse:
        """
        Tạo response cho POST thành công (201)

        Args:
            data: Dữ liệu vừa tạo
            message: Success message

        Returns:
            JSONResponse: 201 Created response
        """
        return APIResponse.success(
            data=data,
            message=message,
            status_code=201
        )

    @staticmethod
    def no_content(message: str = "Thao tác thành công") -> JSONResponse:
        """
        Tạo response cho DELETE/PUT thành công (204)

        Args:
            message: Success message

        Returns:
            JSONResponse: 204 No Content response
        """
        return JSONResponse(
            content={
                "success": True,
                "message": message
            },
            status_code=204
        )


# Utility functions for common responses
def success_response(data: Any = None, message: str = "Thành công") -> JSONResponse:
    """Shortcut cho success response"""
    return APIResponse.success(data=data, message=message)


def error_response(message: str, error_code: str = None, status_code: int = 400) -> JSONResponse:
    """Shortcut cho error response"""
    return APIResponse.error(message=message, error_code=error_code, status_code=status_code)




def unauthorized_response(message: str = "Vui lòng đăng nhập để tiếp tục") -> JSONResponse:
    """Shortcut cho 401 unauthorized - AUTH_001"""
    return APIResponse.error(
        message=message,
        error_code="AUTH_001",
        status_code=401
    )


def forbidden_response(message: str = "Không đủ quyền thực hiện") -> JSONResponse:
    """Shortcut cho 403 forbidden - AUTH_002"""
    return APIResponse.error(
        message=message,
        error_code="AUTH_002",
        status_code=403
    )


def validation_error_response(errors: Dict[str, Any]) -> JSONResponse:
    """Shortcut cho validation error - VALIDATE_001"""
    return APIResponse.error(
        message="Dữ liệu không hợp lệ",
        error_code="VALIDATE_001",
        status_code=422,
        details=errors
    )


def conflict_response(message: str = "Dữ liệu đã tồn tại") -> JSONResponse:
    """Shortcut cho 409 conflict - VALIDATE_002"""
    return APIResponse.error(
        message=message,
        error_code="VALIDATE_002",
        status_code=409
    )


def not_found_response(resource: str = "Tài nguyên") -> JSONResponse:
    """Shortcut cho 404 not found - DATA_001"""
    return APIResponse.error(
        message=f"Không tìm thấy {resource.lower()}",
        error_code="DATA_001",
        status_code=404
    )


# Specific error codes for API contract
def invalid_email_response() -> JSONResponse:
    """Email không hợp lệ - VALIDATE_003"""
    return APIResponse.error(
        message="Email không hợp lệ",
        error_code="VALIDATE_003",
        status_code=400
    )


def invalid_password_response() -> JSONResponse:
    """Password không đủ mạnh - VALIDATE_004"""
    return APIResponse.error(
        message="Password phải có ít nhất 8 ký tự, chứa chữ hoa, chữ thường, số và ký tự đặc biệt",
        error_code="VALIDATE_004",
        status_code=400
    )


def invalid_otp_response() -> JSONResponse:
    """OTP không hợp lệ - AUTH_003"""
    return APIResponse.error(
        message="OTP không hợp lệ hoặc đã hết hạn",
        error_code="AUTH_003",
        status_code=400
    )


def rate_limit_response(retry_after: int = 60) -> JSONResponse:
    """Vượt quá giới hạn request - RATE_001"""
    return APIResponse.error(
        message="Vượt quá giới hạn request cho phép",
        error_code="RATE_001",
        status_code=429
    )


def file_too_large_response(max_size_mb: int = 5) -> JSONResponse:
    """File quá lớn - FILE_001"""
    return APIResponse.error(
        message=f"File không được vượt quá {max_size_mb}MB",
        error_code="FILE_001",
        status_code=400
    )


def invalid_file_type_response(allowed_types: list) -> JSONResponse:
    """Loại file không được hỗ trợ - FILE_002"""
    return APIResponse.error(
        message=f"Chỉ hỗ trợ các định dạng: {', '.join(allowed_types)}",
        error_code="FILE_002",
        status_code=400
    )


def user_blocked_response() -> JSONResponse:
    """Tài khoản đã bị khóa - AUTH_004"""
    return APIResponse.error(
        message="Tài khoản của bạn đã bị khóa",
        error_code="AUTH_004",
        status_code=403
    )


def server_error_response() -> JSONResponse:
    """Lỗi server - SYSTEM_001"""
    return APIResponse.error(
        message="Đã có lỗi xảy ra, vui lòng thử lại sau",
        error_code="SYSTEM_001",
        status_code=500
    )


# Pagination utilities
def create_pagination_info(
    current_page: int,
    total_items: int,
    limit: int
) -> Dict[str, int]:
    """
    Tạo pagination object

    Args:
        current_page: Trang hiện tại
        total_items: Tổng số items
        limit: Items per page

    Returns:
        Dict: Pagination info
    """
    total_pages = (total_items + limit - 1) // limit

    return {
        "current_page": current_page,
        "total_pages": total_pages,
        "total_items": total_items,
        "limit": limit
    }


def paginate_query(
    query: Any,
    page: int = 1,
    limit: int = 10
) -> tuple:
    """
    Apply pagination cho query

    Args:
        query: Database query object
        page: Page number
        limit: Items per page

    Returns:
        tuple: (items, total_items, pagination_info)
    """
    # Calculate offset
    offset = (page - 1) * limit

    # Get total count
    total_items = len(query) if hasattr(query, '__len__') else query.count()

    # Apply pagination
    if hasattr(query, 'offset'):
        items = query.offset(offset).limit(limit).all()
    else:
        items = query[offset:offset + limit]

    # Create pagination info
    pagination = create_pagination_info(page, total_items, limit)

    return items, total_items, pagination