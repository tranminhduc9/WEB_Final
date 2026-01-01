"""
Authentication Service

Service này xử lý logic nghiệp vụ liên quan đến authentication bao gồm:
- User registration với email validation
- User login
- Token management với database storage
- Password handling

Database Schema v3.1 Compatible
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.utils.timezone_helper import utc_now
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
import os

from config.database import User, Role, TokenRefresh, get_db
from middleware.auth import auth_middleware
from middleware.response import (
    conflict_response,
    invalid_email_response,
    invalid_password_response,
    not_found_response
)
from app.utils.email_validator import validate_user_email
from app.utils.image_helpers import get_avatar_url

logger = logging.getLogger(__name__)

# Token expiration
REFRESH_TOKEN_EXPIRATION_DAYS = 7


class AuthService:
    """
    Service xử lý authentication logic with database token storage
    """

    def __init__(self, db: Session):
        """
        Khởi tạo Auth Service

        Args:
            db: Database session
        """
        self.db = db

    # Class-level flag để tránh check roles mỗi lần register
    _roles_checked = False

    def _ensure_roles_exist(self):
        """
        Đảm bảo các roles mặc định tồn tại
        
        Chỉ check 1 lần per session để tránh duplicate queries
        """
        # Skip nếu đã check rồi
        if AuthService._roles_checked:
            return
            
        default_roles = [
            {"id": 1, "role_name": "admin"},
            {"id": 2, "role_name": "moderator"},
            {"id": 3, "role_name": "user"}
        ]
        
        for role_data in default_roles:
            existing = self.db.query(Role).filter(Role.id == role_data["id"]).first()
            if not existing:
                role = Role(**role_data)
                self.db.add(role)
        
        try:
            self.db.commit()
            AuthService._roles_checked = True  # Mark as checked
        except:
            self.db.rollback()


    async def register_user(
        self,
        full_name: str,
        email: str,
        password: str
    ) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Đăng ký user mới với email validation bằng Hunter.io

        Args:
            full_name: Tên đầy đủ
            email: Email
            password: Mật khẩu

        Returns:
            Tuple: (success: bool, response: dict, user_data: dict or None)
        """
        try:
            # Ensure default roles exist
            self._ensure_roles_exist()
            
            # 1. Validate email với Hunter.io
            is_valid, validation_msg, validation_data = await validate_user_email(
                email=email,
                min_score=50  # Score tối thiểu
            )

            # Nếu email không hợp lệ
            if not is_valid:
                logger.warning(f"Email validation failed for {email}: {validation_msg}")
                return False, {
                    "success": False,
                    "error": {
                        "code": "INVALID_EMAIL",
                        "message": validation_msg
                    }
                }, None

            logger.info(f"Email validation passed for {email}: {validation_msg}")

            # 2. Kiểm tra email đã tồn tại chưa
            existing_user = self.db.query(User).filter(User.email == email).first()
            if existing_user:
                logger.warning(f"Registration failed: Email already exists - {email}")
                return False, {
                    "success": False,
                    "error": {
                        "code": "EMAIL_EXISTS",
                        "message": "Email đã được sử dụng"
                    }
                }, None

            # 3. Hash mật khẩu
            password_hash = auth_middleware.hash_password(password)

            # 3.5. Sanitize user inputs
            from app.utils.content_sanitizer import sanitize_full_name
            clean_full_name = sanitize_full_name(full_name)

            # 4. Tạo user mới với role_id (Schema v3.1)
            new_user = User(
                full_name=clean_full_name,
                email=email,
                password_hash=password_hash,
                role_id=3,  # 3 = user role
                is_active=True,
                reputation_score=0,
                created_at=utc_now(),
                updated_at=utc_now()
            )

            # 5. Lưu vào database
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            logger.info(f"User registered successfully: {email} (ID: {new_user.id})")

            # 6. Gửi email chào mừng
            try:
                from middleware.email_service import email_service
                email_sent = await email_service.send_welcome_email(
                    email=email,
                    full_name=full_name
                )
                if email_sent:
                    logger.info(f"Welcome email sent to {email}")
                else:
                    logger.warning(f"Failed to send welcome email to {email}")
            except Exception as e:
                # Không block registration nếu gửi email thất bại
                logger.warning(f"Failed to send welcome email to {email}: {str(e)}")

            # 7. Return success response
            return True, {
                "success": True,
                "message": "Đăng ký thành công! Bạn có thể đăng nhập ngay."
            }, new_user.to_dict()

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error during registration: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "REGISTRATION_ERROR",
                    "message": "Có lỗi xảy ra trong quá trình đăng ký"
                }
            }, None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during registration: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Đã có lỗi xảy ra, vui lòng thử lại sau"
                }
            }, None

    async def login_user(
        self,
        email: str,
        password: str
    ) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Đăng nhập user

        Args:
            email: Email
            password: Mật khẩu

        Returns:
            Tuple: (success: bool, response: dict, user_data: dict or None)
        """
        try:
            # 1. Tìm user theo email
            user = self.db.query(User).filter(User.email == email).first()

            if not user:
                logger.warning(f"Login failed: User not found - {email}")
                return False, {
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Email hoặc mật khẩu không đúng"
                    }
                }, None

            # 2. Kiểm tra user có bị khóa không
            if not user.is_active:
                logger.warning(f"Login failed: User is banned - {email}")
                return False, {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_BANNED",
                        "message": user.ban_reason or "Tài khoản của bạn đã bị khóa"
                    }
                }, None

            # 3. Verify mật khẩu
            if not auth_middleware.verify_password(password, user.password_hash):
                logger.warning(f"Login failed: Invalid password - {email}")
                return False, {
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Email hoặc mật khẩu không đúng"
                    }
                }, None

            # 4. Cập nhật last_login_at
            user.last_login_at = utc_now()
            self.db.commit()

            # 5. Tạo tokens
            access_token = auth_middleware.create_access_token({
                "id": user.id,
                "email": user.email,
                "role": user.role_name,  # Use role_name property
                "role_id": user.role_id
            })

            refresh_token = auth_middleware.create_refresh_token({
                "id": user.id,
                "email": user.email,
                "role": user.role_name,
                "role_id": user.role_id
            })

            # 6. Lưu refresh token vào database (Schema v3.1)
            token_record = TokenRefresh(
                user_id=user.id,
                refresh_token=refresh_token,
                expires_at=utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
                revoked=False
            )
            self.db.add(token_record)
            self.db.commit()

            logger.info(f"User logged in successfully: {email} (ID: {user.id})")

            # 7. Return success response theo Swagger AuthResponse + UserCompact
            return True, {
                "success": True,
                "message": "Đăng nhập thành công",
                "access_token": access_token,
                "user": {
                    "id": user.id,  # Swagger spec: integer, không phải string
                    "full_name": user.full_name,
                    "email": user.email,  # Required for frontend User type
                    "avatar_url": get_avatar_url(user.avatar_url),
                    "role_id": user.role_id,
                    "role": user.role_name  # Frontend checks this field first
                }
            }, user.to_dict(include_sensitive=True)

        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Đã có lỗi xảy ra, vui lòng thử lại sau"
                }
            }, None

    async def refresh_token(
        self,
        refresh_token: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Refresh access token sử dụng refresh token
        Kiểm tra trong database xem token có hợp lệ và chưa bị revoke

        Args:
            refresh_token: Refresh token hiện tại

        Returns:
            Tuple: (success: bool, response: dict)
        """
        try:
            # 1. Kiểm tra token trong database (Schema v3.1)
            token_record = self.db.query(TokenRefresh).filter(
                TokenRefresh.refresh_token == refresh_token,
                TokenRefresh.revoked == False
            ).first()

            if not token_record:
                logger.warning("Refresh token not found in database or revoked")
                return False, {
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Refresh token không hợp lệ hoặc đã bị thu hồi"
                    }
                }

            # 2. Kiểm tra token hết hạn
            if token_record.expires_at < utc_now():
                logger.warning(f"Refresh token expired for user_id={token_record.user_id}")
                # Revoke expired token
                token_record.revoked = True
                self.db.commit()
                return False, {
                    "success": False,
                    "error": {
                        "code": "TOKEN_EXPIRED",
                        "message": "Refresh token đã hết hạn"
                    }
                }

            # 3. Verify JWT token
            payload = await auth_middleware.verify_token(refresh_token, "refresh")

            # 4. Lấy user từ database
            user = self.db.query(User).filter(User.id == token_record.user_id).first()

            if not user:
                return False, {
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Refresh token không hợp lệ"
                    }
                }

            # 5. Kiểm tra user có bị khóa không
            if not user.is_active:
                return False, {
                    "success": False,
                    "error": {
                        "code": "ACCOUNT_BANNED",
                        "message": user.ban_reason or "Tài khoản của bạn đã bị khóa"
                    }
                }

            # 6. Revoke old token (Token Rotation)
            token_record.revoked = True

            # 7. Tạo tokens mới
            new_access_token = auth_middleware.create_access_token({
                "id": user.id,
                "email": user.email,
                "role": user.role_name,
                "role_id": user.role_id
            })

            new_refresh_token = auth_middleware.create_refresh_token({
                "id": user.id,
                "email": user.email,
                "role": user.role_name,
                "role_id": user.role_id
            })

            # 8. Lưu new refresh token vào database
            new_token_record = TokenRefresh(
                user_id=user.id,
                refresh_token=new_refresh_token,
                expires_at=utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
                revoked=False
            )
            self.db.add(new_token_record)
            self.db.commit()

            logger.info(f"Token refreshed for user: {user.email} (ID: {user.id})")

            return True, {
                "success": True,
                "access_token": new_access_token,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,  # Required for frontend User type
                    "avatar_url": get_avatar_url(user.avatar_url),
                    "role_id": user.role_id,
                    "role": user.role_name  # Frontend checks this field first
                }
            }

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Refresh token không hợp lệ hoặc đã hết hạn"
                }
            }

    async def logout_user(self, user_id: int, refresh_token: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Đăng xuất user - Revoke tokens trong database

        Args:
            user_id: ID của user
            refresh_token: Refresh token cần revoke (optional)

        Returns:
            Tuple: (success: bool, response: dict)
        """
        try:
            if refresh_token:
                # Revoke specific token
                token_record = self.db.query(TokenRefresh).filter(
                    TokenRefresh.user_id == user_id,
                    TokenRefresh.refresh_token == refresh_token
                ).first()
                
                if token_record:
                    token_record.revoked = True
                    self.db.commit()
            else:
                # Revoke all tokens for user
                self.db.query(TokenRefresh).filter(
                    TokenRefresh.user_id == user_id,
                    TokenRefresh.revoked == False
                ).update({"revoked": True})
                self.db.commit()
            
            logger.info(f"User logged out: ID {user_id}")

            return True, {
                "success": True,
                "message": "Đăng xuất thành công"
            }

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Đã có lỗi xảy ra"
                }
            }

    async def get_current_user(self, user_id: int) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Lấy thông tin user hiện tại

        Args:
            user_id: ID của user

        Returns:
            Tuple: (success: bool, response: dict, user_data: dict or None)
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user:
                return False, {
                    "success": False,
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": "Không tìm thấy người dùng"
                    }
                }, None

            # Return success response theo Swagger UserCompact format
            return True, {
                "success": True,
                "user": {
                    "id": user.id,  # Swagger spec: integer
                    "full_name": user.full_name,
                    "email": user.email,  # Required for frontend User type
                    "avatar_url": get_avatar_url(user.avatar_url),
                    "role_id": user.role_id,
                    "role": user.role_name  # Frontend checks this field first
                }
            }, user.to_dict()

        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return False, {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Đã có lỗi xảy ra"
                }
            }, None


# ==================== UTILITY FUNCTIONS ====================

def get_auth_service(db: Session) -> AuthService:
    """
    Factory function để lấy Auth Service instance

    Args:
        db: Database session

    Returns:
        AuthService: Auth service instance
    """
    return AuthService(db)
