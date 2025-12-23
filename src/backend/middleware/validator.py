"""
Input Validation Middleware

Module này cung cấp validation cho JSON và FormData inputs
để đảm bảo data integrity và security.
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import Request, HTTPException, UploadFile, Form
from pydantic import BaseModel, ValidationError
import re
import logging

logger = logging.getLogger(__name__)


class ValidationRule:
    """Class định nghĩa validation rules"""

    @staticmethod
    def email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+(?<!\.)\.[a-zA-Z]{2,}$'
        # Additional check: no consecutive dots
        if '..' in email:
            return False
        return bool(re.match(pattern, email))

    @staticmethod
    def password(password: str) -> bool:
        """
        Validate password strength theo API contract

        Requirements:
        - At least 8 characters
        - Contains uppercase, lowercase, number
        - Contains special character: !@#$%^&*(),.?":{}|<>
        """
        if len(password) < 8:
            return False

        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        return has_upper and has_lower and has_digit and has_special

    @staticmethod
    def phone_number(phone: str) -> bool:
        """Validate Vietnamese phone number"""
        # Accept: 0123456789, 09xxxxxxxx, +84xxxxxxxx, etc.
        pattern = r'^(0|\+84)\d{9,10}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def file_size(file: UploadFile, max_size_mb: int = 5) -> bool:
        """Validate file size theo API contract (< 5MB)"""
        if hasattr(file, 'size') and file.size:
            return file.size <= max_size_mb * 1024 * 1024
        return True  # Skip validation if size not available

    @staticmethod
    def file_type(file: UploadFile, allowed_types: List[str] = None) -> bool:
        """Validate file type theo API contract (chỉ .jpg, .png)"""
        # Default allowed types theo API contract
        if allowed_types is None:
            allowed_types = ['jpg', 'jpeg', 'png']

        # Handle Mock objects in tests
        if hasattr(file, 'filename') and not file.filename:
            return False
        elif not hasattr(file, 'filename'):
            return False

        file_extension = file.filename.lower().split('.')[-1]
        return file_extension in [ext.lower() for ext in allowed_types]


class RequestValidator:
    """Class validate request data"""

    def __init__(self):
        self.rules = ValidationRule()

    async def validate_json(
        self,
        request: Request,
        schema: BaseModel,
        required_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate JSON request body

        Args:
            request: FastAPI request
            schema: Pydantic schema for validation
            required_fields: List of required field names

        Returns:
            Dict: Validated data

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Get JSON body
            body = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Request body must be valid JSON"
            )

        # Check required fields
        if required_fields:
            missing_fields = [field for field in required_fields if field not in body]
            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )

        # Validate with Pydantic schema
        try:
            validated_data = schema(**body)
            return validated_data.dict()
        except ValidationError as e:
            error_details = {}
            for error in e.errors():
                field = ".".join(str(loc) for loc in error.get("loc", []))
                error_details[field] = error.get("msg", "Invalid value")

            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Validation failed",
                    "errors": error_details
                }
            )

    async def validate_form_data(
        self,
        request: Request,
        required_fields: Optional[List[str]] = None,
        file_validations: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Validate form data including file uploads

        Args:
            request: FastAPI request
            required_fields: List of required field names
            file_validations: File validation rules

        Returns:
            Dict: Validated form data

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Get form data
            form = await request.form()
            data = {}

            # Process regular fields
            for key, value in form.items():
                if hasattr(value, 'filename'):  # It's a file
                    data[key] = value
                else:  # It's a regular field
                    data[key] = value

            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required fields: {', '.join(missing_fields)}"
                    )

            # Validate files if specified
            if file_validations:
                for field_name, validation_rules in file_validations.items():
                    if field_name in data:
                        file = data[field_name]
                        if not isinstance(file, UploadFile):
                            continue

                        # Validate file size
                        max_size = validation_rules.get("max_size_mb", 5)
                        if not self.rules.file_size(file, max_size):
                            raise HTTPException(
                                status_code=400,
                                detail=f"File {field_name} exceeds maximum size of {max_size}MB"
                            )

                        # Validate file type
                        allowed_types = validation_rules.get("allowed_types", [])
                        if allowed_types and not self.rules.file_type(file, allowed_types):
                            raise HTTPException(
                                status_code=400,
                                detail=f"File {field_name} must be one of: {', '.join(allowed_types)}"
                            )

            return data

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Form validation error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid form data"
            )

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        return self.rules.email(email)

    def validate_password(self, password: str) -> bool:
        """Validate password strength"""
        return self.rules.password(password)

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        return self.rules.phone_number(phone)


# Global validator instance
validator = RequestValidator()


# Decorators for validation
def validate_json(schema: BaseModel, required_fields: Optional[List[str]] = None):
    """
    Decorator for JSON validation

    Args:
        schema: Pydantic schema
        required_fields: Required field names
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            validated_data = await validator.validate_json(
                request, schema, required_fields
            )
            # Add validated data to kwargs
            kwargs['validated_data'] = validated_data
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_form_data(
    required_fields: Optional[List[str]] = None,
    file_validations: Optional[Dict[str, Dict[str, Any]]] = None
):
    """
    Decorator for form data validation

    Args:
        required_fields: Required field names
        file_validations: File validation rules
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            validated_data = await validator.validate_form_data(
                request, required_fields, file_validations
            )
            # Add validated data to kwargs
            kwargs['validated_data'] = validated_data
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# Common validation schemas
class UserRegistrationSchema(BaseModel):
    """Schema for user registration"""
    full_name: str
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "email": "nguyenvana@gmail.com",
                "password": "Password@123"
            }
        }


class UserLoginSchema(BaseModel):
    """Schema for user login"""
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@gmail.com",
                "password": "Password@123"
            }
        }


class RefreshTokenSchema(BaseModel):
    """Schema for refresh token"""
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ForgotPasswordSchema(BaseModel):
    """Schema for forgot password"""
    email: str

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@gmail.com"
            }
        }


class ResetPasswordSchema(BaseModel):
    """Schema for reset password"""
    email: str
    otp: str
    new_password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "nguyenvana@gmail.com",
                "otp": "123456",
                "new_password": "NewPassword@123"
            }
        }


class ChangePasswordSchema(BaseModel):
    """Schema for change password"""
    current_password: str
    new_password: str

    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword@123",
                "new_password": "NewPassword@123"
            }
        }


class UpdateProfileSchema(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "full_name": "Nguyen Van B",
                "bio": "I love traveling in Hanoi",
                "avatar": "https://example.com/avatar.jpg"
            }
        }


class FavoritePlaceSchema(BaseModel):
    """Schema for adding place to favorites"""
    place_id: int

    class Config:
        schema_extra = {
            "example": {
                "place_id": 123
            }
        }


class CreatePostSchema(BaseModel):
    """Schema for creating new post"""
    title: str
    content: str
    cover_image: Optional[str] = None
    related_place_id: Optional[int] = None
    tags: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Trải nghiệm mùa thu Hà Nội",
                "content": "<p>Hôm nay trời rất đẹp...</p>",
                "cover_image": "https://example.com/image.jpg",
                "related_place_id": 50,
                "tags": ["Mùa thu", "Check-in"]
            }
        }


class CreateCommentSchema(BaseModel):
    """Schema for creating comment"""
    content: str

    class Config:
        schema_extra = {
            "example": {
                "content": "Bài viết rất hay và hữu ích!"
            }
        }


class CreateReportSchema(BaseModel):
    """Schema for creating report"""
    target_type: str  # post, review, user
    target_id: Union[int, str]
    reason: str  # spam, offensive, fake_news
    description: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "target_type": "post",
                "target_id": 123,
                "reason": "spam",
                "description": "Spam link cờ bạc"
            }
        }


class ChatbotMessageSchema(BaseModel):
    """Schema for chatbot message"""
    message: str
    history: Optional[List[Dict[str, Any]]] = None

    class Config:
        schema_extra = {
            "example": {
                "message": "Tôi muốn đi chơi Hà Nội 1 ngày với 500k",
                "history": []
            }
        }