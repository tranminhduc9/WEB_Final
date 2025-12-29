"""
Authentication API Routes

Module này định nghĩa các API endpoints cho authentication bao gồm:
- POST /auth/register - Đăng ký user mới
- POST /auth/login - Đăng nhập
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Đăng xuất
- GET /auth/me - Lấy thông tin user hiện tại
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
import logging

from config.database import get_db
from middleware.auth import get_current_user
from middleware.rate_limit import apply_rate_limit
from app.services.auth_service import get_auth_service
from middleware.response import (
    success_response,
    error_response,
    unauthorized_response,
    not_found_response,
    server_error_response
)
# Secure cookies for enhanced security
from middleware.secure_cookies import (
    set_auth_cookies,
    clear_auth_cookies,
    CookieConfig
)
# Request throttling for brute force protection
from middleware.throttle import (
    apply_throttle,
    record_failed_attempt,
    record_successful_attempt,
    get_throttle_status
)
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# Tạo router cho auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== REQUEST SCHEMAS ====================

class RegisterRequest(BaseModel):
    """Schema cho yêu cầu đăng ký"""
    full_name: str = Field(..., min_length=2, max_length=100, description="Tên đầy đủ")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Mật khẩu (ít nhất 6 ký tự)"
    )

    @validator('password')
    def validate_password_strength(cls, v):
        """
        Validate password strength
        - Ít nhất 6 ký tự (đồng bộ với frontend)
        """
        if len(v) < 6:
            raise ValueError('Mật khẩu phải có ít nhất 6 ký tự')

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "full_name": "Nguyen Van A",
                "email": "nguyenvana@gmail.com",
                "password": "abc123"
            }]
        }
    }


class LoginRequest(BaseModel):
    """Schema cho yêu cầu đăng nhập"""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=1, description="Mật khẩu")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "email": "nguyenvana@gmail.com",
                "password": "abc123"
            }]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema cho yêu cầu refresh token"""
    refresh_token: str = Field(..., description="Refresh token")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }]
        }
    }


# ==================== RESPONSES SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Schema cho phản hồi lỗi"""
    success: bool = False
    error: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "success": False,
                "error": {
                    "code": "INVALID_EMAIL",
                    "message": "Email is not deliverable"
                }
            }]
        }
    }


# ==================== ENDPOINTS ====================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(apply_rate_limit)],
    responses={
        201: {"description": "Registration successful"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Register new user",
    description="Đăng ký user mới với email validation bằng Hunter.io. Rate limit: 5 requests/minute"
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
            # Frontend chỉ cần success + message (BaseResponse)
            # KHÔNG cần user data vì không auto-login sau register
            return response
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


@router.get(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Email verified"},
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid or expired token"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Verify Email",
    description="Xác thực email với token được gửi qua email"
)
async def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Xác thực email
    
    **Flow:**
    1. Decode và verify token
    2. Tìm user theo token
    3. Cập nhật email_verified = True
    4. Return success
    
    **Query Parameters:**
    - token: Token xác thực từ email
    
    **Responses:**
    - 200: Xác thực thành công
    - 400: Token không hợp lệ hoặc hết hạn
    - 500: Internal server error
    """
    try:
        from config.database import User
        import jwt
        import os
        
        if not token:
            return error_response(
                message="Token không được để trống",
                error_code="MISSING_TOKEN",
                status_code=400
            )
        
        # Decode token
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            token_type = payload.get("type")
            
            if token_type != "email_verification":
                return error_response(
                    message="Token không hợp lệ",
                    error_code="INVALID_TOKEN",
                    status_code=400
                )
                
        except jwt.ExpiredSignatureError:
            return error_response(
                message="Token đã hết hạn",
                error_code="TOKEN_EXPIRED",
                status_code=400
            )
        except jwt.InvalidTokenError:
            return error_response(
                message="Token không hợp lệ",
                error_code="INVALID_TOKEN",
                status_code=400
            )
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="Người dùng không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=400
            )
        
        # Check if already verified
        if user.email_verified:
            return success_response(message="Email đã được xác thực trước đó")
        
        # Update user
        user.email_verified = True
        db.commit()
        
        logger.info(f"Email verified for user {user.id}")
        
        return success_response(message="Xác thực email thành công")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in verify_email: {str(e)}")
        return server_error_response()


@router.post(

    "/login",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(apply_rate_limit)],
    responses={
        200: {"description": "Login successful"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="User Login",
    description="Đăng nhập với email và mật khẩu. Rate limit: 5 requests/minute"
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
        # Áp dụng throttle - delay nếu có nhiều lần thất bại
        await apply_throttle(request, identifier=login_data.email)
        
        # Lấy auth service
        auth_service = get_auth_service(db)

        # Gọi service để đăng nhập
        success, response, user_data = await auth_service.login_user(
            email=login_data.email,
            password=login_data.password
        )

        # Xử lý kết quả - Return trực tiếp response từ service (đã đúng format)
        if success:
            # Service đã return format frontend cần: {success, message, access_token, refresh_token, user}
            # Tạo JSONResponse để có thể set cookies
            json_response = JSONResponse(content=response)
            
            # Set secure cookies cho authentication
            access_token = response.get("access_token")
            refresh_token = response.get("refresh_token")
            
            if access_token:
                set_auth_cookies(
                    response=json_response,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                logger.info(f"Secure auth cookies set for user: {login_data.email}")
            
            # Reset throttle sau khi login thành công
            record_successful_attempt(request, identifier=login_data.email)
            
            return json_response
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

            # Ghi nhận thất bại nếu là lỗi xác thực
            if error_code == "INVALID_CREDENTIALS":
                record_failed_attempt(request, identifier=login_data.email)
                
                # Thêm thông tin về throttle status vào response
                throttle_info = get_throttle_status(request, identifier=login_data.email)
                remaining_attempts = throttle_info["max_attempts"] - throttle_info["attempts"]
                
                if remaining_attempts > 0:
                    error_message += f" Còn {remaining_attempts} lần thử."
                else:
                    error_message = f"Tài khoản đã bị khóa. Vui lòng thử lại sau {throttle_info['remaining_lockout'] // 60} phút."
                    http_status = 429

            return error_response(
                message=error_message,
                error_code=error_code,
                status_code=http_status
            )

    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}")
        return server_error_response()


@router.post(
    "/refresh",  # Frontend expects /auth/refresh (not /refresh-token)
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(apply_rate_limit)],
    responses={
        200: {"description": "Token refreshed"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Refresh Access Token",
    description="Lấy access token mới sử dụng refresh token. Rate limit: 20 requests/minute"
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

        # Xử lý kết quả - Return theo Swagger AuthResponse format
        if success:
            # Swagger spec: { success, access_token, user? }
            return {
                "success": True,
                "access_token": response["access_token"],
                "user": response.get("user")  # Optional user in refresh
            }
        else:
            # Error case - theo Swagger ErrorResponse format
            error_code = response.get("error", {}).get("code", "INVALID_TOKEN")
            error_message = response.get("error", {}).get("message", "Token không hợp lệ")

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
    dependencies=[Depends(apply_rate_limit)],
    responses={
        200: {"description": "Logout successful"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Logout",
    description="Đăng xuất (xóa tokens ở client-side). Rate limit: 20 requests/minute"
)
async def logout(
    request: Request,
    refresh_data: Optional[RefreshTokenRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Đăng xuất user - Theo Swagger spec KHÔNG yêu cầu authentication

    **Flow:**
    1. Nhận refresh_token từ body (optional)
    2. Revoke refresh token trong database nếu có
    3. Return success

    **Note:** Client cần xóa access token và refresh token ở local

    **Responses:**
    - 200: Đăng xuất thành công
    - 500: Internal server error
    """
    try:
        # Nếu có refresh_token, revoke nó
        if refresh_data and refresh_data.refresh_token:
            # Lấy auth service
            auth_service = get_auth_service(db)
            
            # Tìm và revoke token trong database
            from config.database import TokenRefresh
            token_record = db.query(TokenRefresh).filter(
                TokenRefresh.refresh_token == refresh_data.refresh_token
            ).first()
            
            if token_record:
                token_record.revoked = True
                db.commit()
                logger.info(f"Token revoked for user_id: {token_record.user_id}")

        # Tạo response và xóa authentication cookies
        json_response = JSONResponse(content={
            "success": True,
            "message": "Đăng xuất thành công"
        })
        
        # Clear all auth cookies (Secure, HttpOnly)
        clear_auth_cookies(json_response)
        logger.info("Auth cookies cleared on logout")
        
        return json_response

    except Exception as e:
        logger.error(f"Unexpected error in logout endpoint: {str(e)}")
        return server_error_response()


# NOTE: /auth/me endpoint removed to match Swagger spec
# Users should use /users/me instead (defined in users.py)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(apply_rate_limit)],
    responses={
        200: {"description": "Email sent"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Request Password Reset",
    description="Gửi email reset password. Rate limit: 3 requests/minute"
)
async def forgot_password(
    request: Request,
    email_data: dict,
    db: Session = Depends(get_db)
):
    """
    Yêu cầu reset password
    
    **Flow:**
    1. Validate email
    2. Kiểm tra email tồn tại
    3. Tạo reset token (JWT, 1h expiry)
    4. Gửi email với reset link
    
    **Note:** Luôn return success để tránh email enumeration
    """
    try:
        from config.database import User
        from middleware.email_service import email_service
        import jwt
        import os
        from datetime import datetime, timedelta
        
        email = email_data.get("email", "")
        
        # Find user (không báo lỗi nếu không tìm thấy để tránh email enumeration)
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Generate reset token (1 hour expiry)
            secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
            payload = {
                "user_id": user.id,
                "email": email,
                "type": "password_reset",
                "exp": datetime.utcnow() + timedelta(hours=1)
            }
            reset_token = jwt.encode(payload, secret_key, algorithm="HS256")
            
            # Build reset URL
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url}/reset-password?token={reset_token}&email={email}"
            
            # Send email with reset link
            try:
                await email_service.send_custom_email(
                    to_email=email,
                    subject="Đặt lại mật khẩu - Hanoi Travel",
                    message=f"""
                    <h2>Yêu cầu đặt lại mật khẩu</h2>
                    <p>Xin chào {user.full_name},</p>
                    <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                    <p><a href="{reset_url}" style="background:#3498db;color:white;padding:12px 24px;text-decoration:none;border-radius:5px;">Đặt lại mật khẩu</a></p>
                    <p>Hoặc copy link: {reset_url}</p>
                    <p><strong>Lưu ý:</strong> Link có hiệu lực trong 1 giờ.</p>
                    <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
                    """,
                    is_html=True
                )
                logger.info(f"Password reset email sent to {email}")
            except Exception as e:
                logger.warning(f"Failed to send reset email: {str(e)}")
        
        # Always return success
        return success_response(
            message="Nếu email tồn tại, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu"
        )
        
    except Exception as e:
        logger.error(f"Error in forgot_password: {str(e)}")
        return server_error_response()



@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(apply_rate_limit)],
    responses={
        200: {"description": "Password reset"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    },
    summary="Reset Password",
    description="Reset password với token từ email. Rate limit: 3 requests/minute"
)
async def reset_password(
    request: Request,
    reset_data: dict,
    db: Session = Depends(get_db)
):
    """
    Reset password với token từ email
    
    **Flow:**
    1. Validate email, token, new_password
    2. Decode và verify JWT token
    3. Verify email khớp với token
    4. Update password
    
    **Required fields (per Swagger v1.0.5):**
    - email: Email của user
    - token: JWT token từ email link
    - new_password: Mật khẩu mới (min 6 ký tự)
    """

    try:
        from config.database import User
        from middleware.auth import auth_middleware
        import jwt
        import os
        
        email = reset_data.get("email", "")
        token = reset_data.get("token", "")
        new_password = reset_data.get("new_password", "")
        
        # Validate inputs (Swagger: email, token, new_password required)
        if not email or not token or not new_password:
            return error_response(
                message="Thiếu thông tin bắt buộc (email, token, new_password)",
                error_code="BAD_REQUEST",
                status_code=400
            )
        
        if len(new_password) < 6:
            return error_response(
                message="Mật khẩu phải có ít nhất 6 ký tự",
                error_code="INVALID_PASSWORD",
                status_code=400
            )
        
        # Verify JWT token
        secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            token_email = payload.get("email")
            token_type = payload.get("type")
            
            if token_type != "password_reset":
                return error_response(
                    message="Token không hợp lệ",
                    error_code="INVALID_TOKEN",
                    status_code=400
                )
            
            # Verify email matches token
            if token_email and token_email != email:
                return error_response(
                    message="Email không khớp với token",
                    error_code="INVALID_TOKEN",
                    status_code=400
                )
                
        except jwt.ExpiredSignatureError:
            return error_response(
                message="Link đã hết hạn. Vui lòng yêu cầu đặt lại mật khẩu mới.",
                error_code="TOKEN_EXPIRED",
                status_code=400
            )
        except jwt.InvalidTokenError:
            return error_response(
                message="Token không hợp lệ",
                error_code="INVALID_TOKEN",
                status_code=400
            )
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="Người dùng không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=400
            )
        
        # Update password
        user.password_hash = auth_middleware.hash_password(new_password)
        db.commit()
        
        logger.info(f"Password reset successfully for user {user.id}")
        
        return success_response(message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập với mật khẩu mới.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in reset_password: {str(e)}")
        return server_error_response()



# ==================== END OF AUTH ROUTES ====================
