"""
Input Validation Middleware

Module này cung cấp validation cho JSON và FormData inputs
để đảm bảo data integrity và security.
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import Request, HTTPException, UploadFile, Form
from pydantic import BaseModel, ValidationError, validator as pydantic_validator
import re
import logging
import html
import json
import base64
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Enhanced security validation for XSS and SQL injection prevention"""

    @staticmethod
    def sanitize_input(input_data: Any) -> Any:
        """
        Sanitize input data to prevent XSS attacks

        Args:
            input_data: Input data to sanitize (string, dict, list)

        Returns:
            Sanitized data
        """
        if isinstance(input_data, str):
            # HTML escape to prevent XSS
            escaped = html.escape(input_data)
            # Remove potential script tags
            escaped = re.sub(r'<script.*?>.*?</script.*?>', '', escaped, flags=re.IGNORECASE | re.DOTALL)
            # Remove JavaScript event handlers
            escaped = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', escaped, flags=re.IGNORECASE)
            return escaped
        elif isinstance(input_data, dict):
            return {key: SecurityValidator.sanitize_input(value) for key, value in input_data.items()}
        elif isinstance(input_data, list):
            return [SecurityValidator.sanitize_input(item) for item in input_data]
        else:
            return input_data

    @staticmethod
    def detect_sql_injection(input_data: str) -> bool:
        """
        Detect potential SQL injection attempts

        Args:
            input_data: String to check

        Returns:
            bool: True if SQL injection detected
        """
        if not isinstance(input_data, str):
            return False

        # Common SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|#|/\*|\*/)',
            r'(\bOR\b.*?=.*?=|\bAND\b.*?=.*?=)',
            r'(\bWHERE\b.*\bOR\b)',
            r'(\'\s*OR\s*\'.*\'.*=|\'.*\s*OR\s*.*?=.*?=)',
            r';\s*(DROP|DELETE|UPDATE|INSERT)',
            r'(?i)script\s*>',
            r'(?i)javascript\s*:'
        ]

        input_lower = input_data.lower()
        for pattern in sql_patterns:
            if re.search(pattern, input_lower):
                return True
        return False

    @staticmethod
    def detect_xss(input_data: str) -> bool:
        """
        Detect potential XSS attempts

        Args:
            input_data: String to check

        Returns:
            bool: True if XSS detected
        """
        if not isinstance(input_data, str):
            return False

        # XSS patterns
        xss_patterns = [
            r'<script[^>]*>.*?</script[^>]*>',
            r'javascript\s*:',
            r'vbscript\s*:',
            r'onload\s*=\s*["\'][^"\']*["\']',
            r'onerror\s*=\s*["\'][^"\']*["\']',
            r'onclick\s*=\s*["\'][^"\']*["\']',
            r'onmouseover\s*=\s*["\'][^"\']*["\']',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'eval\s*\(',
            r'expression\s*\('
        ]

        input_lower = input_data.lower()
        for pattern in xss_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def validate_file_content_security(file_content: bytes) -> bool:
        """
        Validate file content for security threats

        Args:
            file_content: File content as bytes

        Returns:
            bool: True if file is safe
        """
        try:
            # Check for executable file signatures
            executable_signatures = [
                b'\x4D\x5A',  # PE/Windows executable
                b'\x7FELF',  # Linux executable
                b'\xCA\xFE\xBA\xBE',  # Java class
                b'\xFE\xED\xFA',  # Mach-O binary
            ]

            for signature in executable_signatures:
                if file_content.startswith(signature):
                    return False

            # Check for script content in image files
            if file_content.startswith(b'\xFF\xD8\xFF'):  # JPEG
                if b'<script' in file_content.lower():
                    return False
            elif file_content.startswith(b'\x89PNG'):  # PNG
                if b'<script' in file_content.lower():
                    return False

            return True

        except Exception:
            # If we can't validate, err on the side of caution
            return False

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate filename for path traversal attempts

        Args:
            filename: Filename to validate

        Returns:
            bool: True if filename is safe
        """
        if not filename:
            return False

        # Check for path traversal
        dangerous_patterns = [
            r'\.\./',
            r'\.\\.\\',
            r'^[/\\]',
            r'[/\\]$',
            r'\x00',  # Null byte
            r'[<>:"|?*]',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, filename):
                return False

        # Check length
        if len(filename) > 255:
            return False

        return True


class ValidationRule:
    """Class định nghĩa validation rules"""

    @staticmethod
    def email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
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
        if not password or not isinstance(password, str) or len(password) < 8:
            return False

        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        return has_upper and has_lower and has_digit and has_special

    @staticmethod
    def phone_number(phone: str) -> bool:
        """Validate Vietnamese phone number"""
        if not phone or not isinstance(phone, str):
            return False
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

        # Validate filename security first
        if not SecurityValidator.validate_filename(file.filename):
            return False

        file_extension = file.filename.lower().split('.')[-1]
        return file_extension in [ext.lower() for ext in allowed_types]

    @staticmethod
    def file_content_security(file: UploadFile, max_size_mb: int = 5) -> bool:
        """
        Validate file content for security threats

        Args:
            file: UploadFile object
            max_size_mb: Maximum file size in MB

        Returns:
            bool: True if file is safe
        """
        try:
            # Check file size first
            if hasattr(file, 'size') and file.size:
                if file.size > max_size_mb * 1024 * 1024:
                    return False

            # Read file content for security validation
            content = file.file.read(1024)  # Read first 1KB for security check
            file.file.seek(0)  # Reset file pointer

            if not SecurityValidator.validate_file_content_security(content):
                return False

            return True

        except Exception:
            # If we can't validate, err on the side of caution
            return False


class RequestValidator:
    """Class validate request data"""

    def __init__(self):
        self.rules = ValidationRule()

    async def validate_json(
        self,
        request: Request,
        schema: BaseModel,
        required_fields: Optional[List[str]] = None,
        security_check: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced JSON validation with security checks

        Args:
            request: FastAPI request
            schema: Pydantic schema for validation
            required_fields: List of required field names
            security_check: Whether to perform security validation

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

        # Security validation
        if security_check:
            await self._validate_request_security(body)

        # Check required fields
        if required_fields:
            missing_fields = [field for field in required_fields if field not in body]
            if missing_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )

        # Sanitize input data
        sanitized_body = SecurityValidator.sanitize_input(body)

        # Validate with Pydantic schema
        try:
            validated_data = schema(**sanitized_body)
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

    async def _validate_request_security(self, data: Dict[str, Any]):
        """Validate request data for security threats"""
        def check_security_recursive(obj, path=""):
            if isinstance(obj, str):
                # Check for SQL injection
                if SecurityValidator.detect_sql_injection(obj):
                    logger.warning(f"SQL injection detected at path: {path}")
                    raise HTTPException(
                        status_code=400,
                        detail="Potential SQL injection detected"
                    )
                # Check for XSS
                if SecurityValidator.detect_xss(obj):
                    logger.warning(f"XSS detected at path: {path}")
                    raise HTTPException(
                        status_code=400,
                        detail="Potential XSS attack detected"
                    )
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_security_recursive(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_security_recursive(item, f"{path}[{i}]")

        check_security_recursive(data)

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

    @pydantic_validator('email')
    def validate_email(cls, v):
        if not ValidationRule().email(v):
            raise ValueError('Invalid email format')
        return v

    @pydantic_validator('password')
    def validate_password(cls, v):
        if not ValidationRule().password(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, digit, and special character')
        return v

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


class LogoutSchema(BaseModel):
    """Schema for logout"""
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class GetFavoritesQuerySchema(BaseModel):
    """Schema for get favorites query params"""
    page: Optional[int] = 1
    limit: Optional[int] = 10

    @pydantic_validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v

    @pydantic_validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 10
            }
        }


class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    url: str
    public_id: str
    format: Optional[str] = None
    size: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
                "public_id": "hanoi-travel/avatars/123/abc123",
                "format": "jpg",
                "size": 1024000
            }
        }


class UserStatsResponse(BaseModel):
    """Schema for user stats in profile"""
    posts_count: int = 0
    places_visited: int = 0
    favorites_count: int = 0
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0

    class Config:
        schema_extra = {
            "example": {
                "posts_count": 15,
                "places_visited": 42,
                "favorites_count": 8
            }
        }


class PublicUserProfileResponse(BaseModel):
    """Schema for public user profile response"""
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    reputation_score: int = 0
    stats: UserStatsResponse
    recent_posts: Optional[List[dict]] = []

    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "full_name": "Nguyen Van A",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "I love Hanoi",
                "reputation_score": 150,
                "stats": {
                    "posts_count": 15,
                    "places_visited": 42,
                    "favorites_count": 8
                },
                "recent_posts": []
            }
        }