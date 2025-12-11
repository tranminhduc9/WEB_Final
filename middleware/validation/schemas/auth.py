"""
Authentication validation schemas.

Pydantic schemas for validating authentication-related requests.
Implementation following Task #4 validation requirements.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, validator


class RegisterSchema(BaseModel):
    """
    Schema for user registration validation.

    Rules:
    - full_name: 2-50 characters, required
    - email: valid email format, required
    - password: min 8 chars, must have uppercase, lowercase, number, special char
    - phone: optional, format 0xxxxxxxxx (10 digits)
    """

    full_name: str = Field(..., min_length=2, max_length=50, description="Full name of the user")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    phone: Optional[str] = Field(None, description="User phone number")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Email không hợp lệ')
        return v.lower().strip()

    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Mật khẩu phải chứa ít nhất một chữ hoa')
        if not re.search(r'[a-z]', v):
            raise ValueError('Mật khẩu phải chứa ít nhất một chữ thường')
        if not re.search(r'[0-9]', v):
            raise ValueError('Mật khẩu phải chứa ít nhất một số')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Mật khẩu phải chứa ít nhất một ký tự đặc biệt')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v

        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', v)

        # Check if it's a valid Vietnamese phone number (10 digits starting with 0)
        if not re.match(r'^0\d{9}$', phone_digits):
            raise ValueError('Số điện thoại không hợp lệ. Phải có 10 chữ số bắt đầu bằng 0')

        return phone_digits

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name."""
        # Remove extra whitespace and check if name is not empty after cleaning
        cleaned_name = ' '.join(v.strip().split())
        if not cleaned_name:
            raise ValueError('Họ và tên không được để trống')
        return cleaned_name

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "email": "nguyenvana@example.com",
                "password": "Password123!",
                "phone": "0912345678"
            }
        }


class LoginSchema(BaseModel):
    """
    Schema for user login validation.

    Rules:
    - email: valid email format, required
    - password: not empty, required
    """

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Email không hợp lệ')
        return v.lower().strip()

    @validator('password')
    def validate_password(cls, v):
        """Validate password is not empty."""
        if not v or v.strip() == '':
            raise ValueError('Mật khẩu không được để trống')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@example.com",
                "password": "password123"
            }
        }


class ChangePasswordSchema(BaseModel):
    """
    Schema for password change validation.
    """

    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password complexity."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một chữ hoa')
        if not re.search(r'[a-z]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một chữ thường')
        if not re.search(r'[0-9]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một số')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một ký tự đặc biệt')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Xác nhận mật khẩu không khớp')
        return v

    class Config:
        schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        }


class ForgotPasswordSchema(BaseModel):
    """
    Schema for forgot password request validation.
    """

    email: str = Field(..., description="User email address")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Email không hợp lệ')
        return v.lower().strip()

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@example.com"
            }
        }


class ResetPasswordSchema(BaseModel):
    """
    Schema for password reset validation.
    """

    token: str = Field(..., description="Password reset token")
    email: str = Field(..., description="User email address")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Email không hợp lệ')
        return v.lower().strip()

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password complexity."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một chữ hoa')
        if not re.search(r'[a-z]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một chữ thường')
        if not re.search(r'[0-9]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một số')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Mật khẩu mới phải chứa ít nhất một ký tự đặc biệt')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Xác nhận mật khẩu không khớp')
        return v

    class Config:
        schema_extra = {
            "example": {
                "token": "reset_token_here",
                "email": "nguyenvana@example.com",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        }


class UpdateProfileSchema(BaseModel):
    """
    Schema for user profile update validation.
    """

    full_name: Optional[str] = Field(None, min_length=2, max_length=50, description="Full name of the user")
    email: Optional[str] = Field(None, description="User email address")
    phone: Optional[str] = Field(None, description="User phone number")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if v is None:
            return v

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Email không hợp lệ')
        return v.lower().strip()

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v

        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', v)

        # Check if it's a valid Vietnamese phone number (10 digits starting with 0)
        if not re.match(r'^0\d{9}$', phone_digits):
            raise ValueError('Số điện thoại không hợp lệ. Phải có 10 chữ số bắt đầu bằng 0')

        return phone_digits

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name."""
        if v is None:
            return v

        # Remove extra whitespace and check if name is not empty after cleaning
        cleaned_name = ' '.join(v.strip().split())
        if not cleaned_name:
            raise ValueError('Họ và tên không được để trống')
        return cleaned_name

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "email": "newemail@example.com",
                "phone": "0912345678"
            }
        }