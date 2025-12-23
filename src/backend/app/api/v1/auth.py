"""
Authentication API Routes

Module này định nghĩa các API endpoints cho authentication bao gồm:
- POST /auth/register - Đăng ký user mới
- POST /auth/login - Đăng nhập
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Đăng xuất
- GET /users/me - Lấy thông tin user hiện tại
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
import logging

from ....config.database import get_db
from ....middleware.auth import get_current_user
from ....services.auth_service import get_auth_service
from ....middleware.response import (
    success_response,
    error_response,
    unauthorized_response,
    not_found_response,
    server_error_response
)

logger = logging.getLogger(__name__)

# Tạo router cho auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== REQUEST SCHEMAS ====================

class RegisterRequest(BaseModel):
    """Schema cho request đăng ký"""
    full_name: str = Field(..., min_length=2, max_length=100, description="Tên đầy đủ")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Mật khẩu (ít nhất 8 ký tự, chứa chữ hoa, chữ thường, số và ký tự đặc biệt)"
    )

    @validator('password')
    def validate_password_strength(cls, v):
        """
        Validate password strength
        - Ít nhất 8 ký tự
        - Chứa chữ hoa, chữ thường, số
        - Chứa ký tự đặc biệt
        """
        import re

        if len(v) < 8:
            raise ValueError('Mật khẩu phải có ít nhất 8 ký tự')

        has_upper = bool(re.search(r'[A-Z]', v))
        has_lower = bool(re.search(r'[a-z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', v))

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Mật khẩu phải chứa chữ hoa, chữ thường, số và ký tự đặc biệt'
            )

        return v

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "email": "nguyenvana@gmail.com",
                "password": "Password@123"
            }
        }


class LoginRequest(BaseModel):
    """Schema cho request đăng nhập"""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=1, description="Mật khẩu")

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@gmail.com",
                "password": "Password@123"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema cho refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ==================== RESPONSES SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Schema cho error response"""
    success: bool = False
    error: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "INVALID_EMAIL",
                    "message": "Email is not deliverable"
                }
            }
        }


# ==================== ENDPOINTS ====================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Registration successful"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Register new user",
    description="Đăng ký user mới với email validation bằng Hunter.io"
)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Đăng ký user mới

    **Flow:**
    1. Validate email format
    2. Validate email với Hunter.io API
    3. Kiểm tra email đã tồn tại chưa
    4. Hash mật khẩu
    5. Tạo user trong database
    6. Tạo access token và refresh token
    7. Return tokens và user info

    **Responses:**
    - 201: Đăng ký thành công
    - 400: Email không hợp lệ hoặc đã tồn tại
    - 422: Validation error (password không đủ mạnh)
    - 500: Internal server error
    """
    try:
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Gọi service để đăng ký user
        success, response, user_data = await auth_service.register_user(
            full_name=register_data.full_name,
            email=register_data.email,
            password=register_data.password
        )

        # Xử lý kết quả
        if success:
            return success_response(
                data={
                    "access_token": response["access_token"],
                    "user": response["user"]
                },
                message=response["message"],
                status_code=201
            )
        else:
            # Error case
            error_code = response.get("error", {}).get("code", "UNKNOWN_ERROR")
            error_message = response.get("error", {}).get("message", "Đã có lỗi xảy ra")

            # Map error codes sang HTTP status
            status_code_mapping = {
                "INVALID_EMAIL": 400,
                "EMAIL_EXISTS": 400,
                "REGISTRATION_ERROR": 400,
                "INTERNAL_ERROR": 500
            }

            http_status = status_code_mapping.get(error_code, 500)

            return error_response(
                message=error_message,
                error_code=error_code,
                status_code=http_status
            )

    except Exception as e:
        logger.error(f"Unexpected error in register endpoint: {str(e)}")
        return server_error_response()


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="User Login",
    description="Đăng nhập với email và mật khẩu"
)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Đăng nhập user

    **Flow:**
    1. Tìm user theo email
    2. Verify mật khẩu
    3. Kiểm tra tài khoản có bị khóa không
    4. Cập nhật last_login
    5. Tạo access token và refresh token
    6. Return tokens và user info

    **Responses:**
    - 200: Đăng nhập thành công
    - 400: Bad request
    - 401: Email hoặc mật khẩu không đúng
    - 500: Internal server error
    """
    try:
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Gọi service để đăng nhập
        success, response, user_data = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )

        # Xử lý kết quả
        if success:
            return success_response(
                data={
                    "access_token": response["access_token"],
                    "refresh_token": response["refresh_token"],
                    "user": response["user"]
                },
                message=response["message"]
            )
        else:
            # Error case
            error_code = response.get("error", {}).get("code", "UNKNOWN_ERROR")
            error_message = response.get("error", {}).get("message", "Đã có lỗi xảy ra")

            # Map error codes sang HTTP status
            status_code_mapping = {
                "INVALID_CREDENTIALS": 401,
                "ACCOUNT_BANNED": 403,
                "INTERNAL_ERROR": 500
            }

            http_status = status_code_mapping.get(error_code, 400)

            return error_response(
                message=error_message,
                error_code=error_code,
                status_code=http_status
            )

    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}")
        return server_error_response()


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Token refreshed"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Refresh Access Token",
    description="Lấy access token mới sử dụng refresh token"
)
async def refresh_access_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token

    **Flow:**
    1. Verify refresh token
    2. Lấy user từ database
    3. Tạo access token và refresh token mới
    4. Return tokens

    **Responses:**
    - 200: Refresh thành công
    - 401: Refresh token không hợp lệ
    - 500: Internal server error
    """
    try:
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Gọi service để refresh token
        success, response = await auth_service.refresh_token(
            refresh_token=refresh_data.refresh_token
        )

        # Xử lý kết quả
        if success:
            return success_response(
                data={
                    "access_token": response["access_token"],
                    "refresh_token": response["refresh_token"]
                },
                message=response["message"]
            )
        else:
            # Error case
            error_code = response.get("error", {}).get("code", "UNKNOWN_ERROR")
            error_message = response.get("error", {}).get("message", "Đã có lỗi xảy ra")

            return error_response(
                message=error_message,
                error_code=error_code,
                status_code=401
            )

    except Exception as e:
        logger.error(f"Unexpected error in refresh endpoint: {str(e)}")
        return server_error_response()


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Logout",
    description="Đăng xuất (xóa tokens ở client-side)"
)
async def logout(
    request: Request,
    refresh_data: Optional[RefreshTokenRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đăng xuất user

    **Flow:**
    1. Lấy user info từ access token
    2. Log logout action
    3. Return success

    **Note:** Client cần xóa access token và refresh token

    **Responses:**
    - 200: Đăng xuất thành công
    - 500: Internal server error
    """
    try:
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Gọi service để logout
        user_id = int(current_user.get("user_id", 0))
        success, response = await auth_service.logout_user(user_id=user_id)

        # Xử lý kết quả
        if success:
            return success_response(message=response["message"])
        else:
            return server_error_response()

    except Exception as e:
        logger.error(f"Unexpected error in logout endpoint: {str(e)}")
        return server_error_response()


# ==================== USER PROFILE ENDPOINT ====================

# Router cho user profile (không dùng prefix /auth)
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Profile data"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Get Profile",
    description="Lấy thông tin profile của user hiện tại"
)
async def get_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin user hiện tại

    **Flow:**
    1. Verify access token
    2. Lấy user info từ database
    3. Return user profile

    **Responses:**
    - 200: Thành công, return user profile
    - 401: Chưa đăng nhập
    - 500: Internal server error
    """
    try:
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Lấy user ID từ token
        user_id = int(current_user.get("user_id", 0))

        # Gọi service để lấy user info
        success, response, user_data = await auth_service.get_current_user(user_id=user_id)

        # Xử lý kết quả
        if success:
            return success_response(data=response["data"])
        else:
            error_code = response.get("error", {}).get("code", "UNKNOWN_ERROR")
            error_message = response.get("error", {}).get("message", "Đã có lỗi xảy ra")

            if error_code == "USER_NOT_FOUND":
                return not_found_response("người dùng")
            else:
                return server_error_response()

    except Exception as e:
        logger.error(f"Unexpected error in get_profile endpoint: {str(e)}")
        return server_error_response()
