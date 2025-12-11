"""
Request Validation Middleware v2.0 cho WEB Final API

Triển khai request validation với Pydantic schemas cho API v1:
- Validation cho body, query, params
- Support cho file upload validation
- Custom error messages tiếng Việt
- Format chuẩn response theo API contract
"""

import logging
from typing import Dict, List, Any, Optional, Union, Type
from functools import wraps
import re

import pydantic
from fastapi import Request, Response, HTTPException, status, UploadFile
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, ValidationError, validator, Field

logger = logging.getLogger(__name__)


class ValidationException(HTTPException):
    """Custom exception cho Validation errors"""

    def __init__(self, error_code: str, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        # Format theo chuẩn response mới
        self.detail = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "data": details if details else None
        }


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Request Validation Middleware v2.0 cho WEB Final API

    Validates incoming request data theo API contract v1.
    Supports body, query, params validation với detailed error responses.
    """

    def __init__(
        self,
        app,
        endpoint_schemas: Optional[Dict[str, Dict[str, Type[BaseModel]]]] = None,
        excluded_paths: Optional[List[str]] = None,
        strict_mode: bool = True,
    ):
        """
        Initialize Validation Middleware

        Args:
            app: FastAPI application instance
            endpoint_schemas: Mapping endpoint → {body, query, params} schemas
            excluded_paths: Paths excluded from validation
            strict_mode: Enable strict validation mode
        """
        super().__init__(app)

        self.strict_mode = strict_mode

        # Excluded paths từ validation
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/static",
        ]

        # Default schemas theo API v1
        self.endpoint_schemas = endpoint_schemas or self._build_default_schemas()

        # Statistics
        self.stats = {
            "total_requests": 0,
            "validation_errors": 0,
            "validation_passed": 0,
        }

    def _build_default_schemas(self) -> Dict[str, Dict[str, Type[BaseModel]]]:
        """
        Xây dựng default validation schemas theo API contract v1
        """
        schemas = {}

        # Authentication schemas
        schemas["POST:/api/v1/auth/register"] = {
            "body": self.get_register_schema()
        }
        schemas["POST:/api/v1/auth/login"] = {
            "body": self.get_login_schema()
        }
        schemas["POST:/api/v1/auth/forgot-password"] = {
            "body": self.get_forgot_password_schema()
        }
        schemas["POST:/api/v1/auth/reset-password"] = {
            "body": self.get_reset_password_schema()
        }
        schemas["POST:/api/v1/auth/refresh-token"] = {
            "body": self.get_refresh_token_schema()
        }
        schemas["POST:/api/v1/auth/logout"] = {
            "body": self.get_logout_schema()
        }

        # Post schemas
        schemas["POST:/api/v1/posts"] = {
            "body": self.get_create_post_schema()
        }
        schemas["GET:/api/v1/posts"] = {
            "query": self.get_posts_query_schema()
        }

        # User schemas
        schemas["PUT:/api/v1/users/me"] = {
            "body": self.get_update_user_schema()
        }
        schemas["PUT:/api/v1/users/me/password"] = {
            "body": self.get_change_password_schema()
        }

        # Places schemas
        schemas["GET:/api/v1/places"] = {
            "query": self.get_places_query_schema()
        }
        schemas["GET:/api/v1/places/suggest"] = {
            "query": self.get_suggest_query_schema()
        }

        # Favorites schemas
        schemas["POST:/api/v1/favorites/places"] = {
            "body": self.get_add_favorite_schema()
        }

        # Report schemas
        schemas["POST:/api/v1/reports"] = {
            "body": self.get_create_report_schema()
        }

        # Admin schemas
        schemas["POST:/api/v1/admin/places"] = {
            "body": self.get_create_place_schema()
        }
        schemas["PATCH:/api/v1/admin/users/"] = {
            "params": self.get_user_id_schema(),
            "body": self.get_update_user_status_schema()
        }

        return schemas

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và validate data

        Args:
            request: HTTP request cần xử lý
            call_next: Middleware tiếp theo

        Returns:
            HTTP response nếu validation pass, ngược lại raise ValidationException
        """
        try:
            self.stats["total_requests"] += 1

            # Skip validation cho excluded paths
            if self._is_excluded_path(request.url.path):
                return await call_next(request)

            # Get endpoint schemas
            endpoint_key = f"{request.method}:{request.url.path}"
            schemas = self._get_endpoint_schemas(endpoint_key)

            if not schemas:
                # No schemas found, skip validation in non-strict mode
                if not self.strict_mode:
                    self.stats["validation_passed"] += 1
                    return await call_next(request)

            # Validate request
            await self._validate_request(request, schemas)

            self.stats["validation_passed"] += 1
            return await call_next(request)

        except ValidationException:
            raise
        except RequestValidationError as e:
            self.stats["validation_errors"] += 1
            error_details = self._format_validation_errors(e.errors())
            raise ValidationException(
                "VALIDATION_001",
                "Dữ liệu không hợp lệ",
                error_details
            )
        except ValidationError as e:
            self.stats["validation_errors"] += 1
            error_details = self._format_validation_errors(e.errors())
            raise ValidationException(
                "VALIDATION_002",
                "Validation failed",
                error_details
            )
        except Exception as e:
            logger.error(f"Lỗi không mong đợi trong validation middleware: {str(e)}")
            # Fail-open: allow request nếu có lỗi trong validation
            return await call_next(request)

    def _is_excluded_path(self, path: str) -> bool:
        """Kiểm tra path có nên được loại trừ khỏi validation không"""
        if path in self.excluded_paths:
            return True

        for excluded_path in self.excluded_paths:
            if excluded_path.endswith('/') and path.startswith(excluded_path):
                return True
            if excluded_path.endswith('*') and path.startswith(excluded_path[:-1]):
                return True

        return False

    def _get_endpoint_schemas(self, endpoint_key: str) -> Optional[Dict[str, Type[BaseModel]]]:
        """
        Lấy validation schemas cho endpoint

        Args:
            endpoint_key: Endpoint key (METHOD:PATH)

        Returns:
            Schemas dictionary hoặc None
        """
        # Exact match
        if endpoint_key in self.endpoint_schemas:
            return self.endpoint_schemas[endpoint_key]

        # Pattern match cho dynamic endpoints
        for pattern_key, schemas in self.endpoint_schemas.items():
            if self._pattern_match(endpoint_key, pattern_key):
                return schemas

        return None

    def _pattern_match(self, endpoint: str, pattern: str) -> bool:
        """
        Kiểm tra endpoint có match với pattern không
        Ví dụ: "DELETE:/api/v1/admin/posts/123" match "DELETE:/api/v1/admin/posts/"
        """
        if pattern.endswith("/"):
            return endpoint.startswith(pattern)
        return endpoint == pattern

    async def _validate_request(self, request: Request, schemas: Dict[str, Type[BaseModel]]):
        """
        Validate request data theo schemas

        Args:
            request: HTTP request object
            schemas: Validation schemas
        """
        errors = []

        # Validate request body
        if "body" in schemas:
            try:
                if request.method in ["POST", "PUT", "PATCH"]:
                    body_data = await self._get_request_body(request)
                    if body_data:
                        schemas["body"].parse_obj(body_data)
            except ValidationError as e:
                errors.extend(e.errors())

        # Validate query parameters
        if "query" in schemas:
            try:
                query_data = dict(request.query_params)
                if query_data:
                    schemas["query"].parse_obj(query_data)
            except ValidationError as e:
                errors.extend(e.errors())

        # Validate path parameters
        if "params" in schemas:
            try:
                params_data = self._extract_path_params(request)
                if params_data:
                    schemas["params"].parse_obj(params_data)
            except ValidationError as e:
                errors.extend(e.errors())

        # Validate file upload
        if "file" in schemas and hasattr(request, "_form") and request._form:
            try:
                file_data = await self._get_file_data(request)
                if file_data:
                    schemas["file"].parse_obj(file_data)
            except ValidationError as e:
                errors.extend(e.errors())

        if errors:
            raise ValidationError(errors)

    async def _get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract JSON body từ request"""
        try:
            if hasattr(request, '_json'):
                return request._json
            return await request.json()
        except Exception:
            return None

    def _extract_path_params(self, request: Request) -> Dict[str, Any]:
        """Extract path parameters từ request"""
        path_params = {}
        if hasattr(request, 'path_params'):
            path_params = request.path_params
        return path_params

    async def _get_file_data(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract file data từ request"""
        try:
            if hasattr(request, "_form") and request._form:
                form_data = await request.form()
                file_data = {}
                for key, value in form_data.items():
                    if isinstance(value, UploadFile):
                        file_data[key] = {
                            "filename": value.filename,
                            "content_type": value.content_type,
                            "size": 0  # Will be updated when reading
                        }
                return file_data
        except Exception:
            pass
        return None

    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format validation errors theo chuẩn response

        Args:
            errors: Pydantic validation errors

        Returns:
            Formatted error details
        """
        formatted_errors = []
        for error in errors:
            field = ".".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": self._get_vietnamese_error_message(error),
                "value": error.get("input"),
                "type": error["type"]
            })
        return formatted_errors

    def _get_vietnamese_error_message(self, error: Dict[str, Any]) -> str:
        """
        Translate Pydantic error message sang tiếng Việt
        """
        error_type = error["type"]
        field = ".".join(str(loc) for loc in error["loc"])

        # Custom error messages
        messages = {
            "value_error.missing": f"Thiếu trường '{field}'",
            "value_error.not_in": f"Giá trị không hợp lệ cho trường '{field}'",
            "value_error.email": f"Email không hợp lệ",
            "value_error.url": f"URL không hợp lệ",
            "value_error.str.regex": f"Định dạng không hợp lệ cho trường '{field}'",
            "value_error.number.not_ge": f"Giá trị '{field}' phải lớn hơn hoặc bằng {error.get('ctx', {}).get('ge_value', 0)}",
            "value_error.number.not_le": f"Giá trị '{field}' phải nhỏ hơn hoặc bằng {error.get('ctx', {}).get('le_value', 0)}",
            "value_error.number.not_gt": f"Giá trị '{field}' phải lớn hơn {error.get('ctx', {}).get('gt_value', 0)}",
            "value_error.number.not_lt": f"Giá trị '{field}' phải nhỏ hơn {error.get('ctx', {}).get('lt_value', 0)}",
            "value_error.length.missing": f"Thiếu giá trị cho trường '{field}'",
            "value_error.str.length": f"Độ dài của trường '{field}' không hợp lệ",
        }

        return messages.get(error_type, error.get("msg", f"Lỗi validation tại trường '{field}'"))

    # Schema definitions
    @staticmethod
    def get_register_schema():
        """Schema cho user registration"""
        class RegisterSchema(BaseModel):
            full_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên đầy đủ")
            email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email hợp lệ")
            password: str = Field(..., min_length=8, max_length=100, description="Mật khẩu (tối thiểu 8 ký tự)")

            @validator('full_name')
            def validate_full_name(cls, v):
                if not v.strip():
                    raise ValueError('Họ và tên không được để trống')
                return v.strip()

            @validator('password')
            def validate_password(cls, v):
                if not re.search(r'[A-Z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ hoa')
                if not re.search(r'[a-z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ thường')
                if not re.search(r'[0-9]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
                return v

        return RegisterSchema

    @staticmethod
    def get_login_schema():
        """Schema cho user login"""
        class LoginSchema(BaseModel):
            email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email hợp lệ")
            password: str = Field(..., min_length=1, description="Mật khẩu")

        return LoginSchema

    @staticmethod
    def get_forgot_password_schema():
        """Schema cho forgot password"""
        class ForgotPasswordSchema(BaseModel):
            email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email hợp lệ")

        return ForgotPasswordSchema

    @staticmethod
    def get_reset_password_schema():
        """Schema cho reset password"""
        class ResetPasswordSchema(BaseModel):
            email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', description="Email hợp lệ")
            otp: str = Field(..., regex=r'^\d{6}$', description="Mã OTP 6 số")
            new_password: str = Field(..., min_length=8, max_length=100, description="Mật khẩu mới")

            @validator('new_password')
            def validate_password(cls, v):
                if not re.search(r'[A-Z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ hoa')
                if not re.search(r'[a-z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ thường')
                if not re.search(r'[0-9]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
                return v

        return ResetPasswordSchema

    @staticmethod
    def get_refresh_token_schema():
        """Schema cho refresh token"""
        class RefreshTokenSchema(BaseModel):
            refresh_token: str = Field(..., min_length=1, description="Refresh token")

        return RefreshTokenSchema

    @staticmethod
    def get_logout_schema():
        """Schema cho logout"""
        class LogoutSchema(BaseModel):
            refresh_token: str = Field(..., min_length=1, description="Refresh token")

        return LogoutSchema

    @staticmethod
    def get_create_post_schema():
        """Schema cho creating post"""
        class CreatePostSchema(BaseModel):
            title: str = Field(..., min_length=10, max_length=200, description="Tiêu đề bài viết")
            content: str = Field(..., min_length=1, description="Nội dung bài viết")
            cover_image: Optional[str] = Field(None, regex=r'^https?://.+\.(jpg|jpeg|png|gif|webp)$', description="URL ảnh bìa")
            related_place_id: Optional[int] = Field(None, ge=1, description="ID địa điểm liên quan")
            tags: Optional[List[str]] = Field([], description="Thẻ tags (tối đa 5)")

            @validator('title')
            def validate_title(cls, v):
                if not v.strip():
                    raise ValueError('Tiêu đề không được để trống')
                return v.strip()

            @validator('content')
            def validate_content(cls, v):
                if not v.strip():
                    raise ValueError('Nội dung không được để trống')
                return v.strip()

            @validator('tags')
            def validate_tags(cls, v):
                if v and len(v) > 5:
                    raise ValueError('Tối đa 5 thẻ tags được phép')
                return [tag.strip() for tag in v if tag.strip()] if v else []

        return CreatePostSchema

    @staticmethod
    def get_posts_query_schema():
        """Schema cho posts query parameters"""
        class PostsQuerySchema(BaseModel):
            page: Optional[int] = Field(1, ge=1, description="Số trang")
            limit: Optional[int] = Field(10, ge=1, le=100, description="Số items mỗi trang")
            sort: Optional[str] = Field("latest", regex=r'^(latest|oldest|most_liked|most_viewed)$', description="Sắp xếp theo")
            tag: Optional[str] = Field(None, description="Lọc theo tag")
            keyword: Optional[str] = Field(None, description="Từ khóa tìm kiếm")

        return PostsQuerySchema

    @staticmethod
    def get_update_user_schema():
        """Schema cho updating user profile"""
        class UpdateUserSchema(BaseModel):
            full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="Họ và tên")
            bio: Optional[str] = Field(None, max_length=500, description="Tiểu sử")
            avatar: Optional[str] = Field(None, regex=r'^https?://.+\.(jpg|jpeg|png|gif|webp)$', description="URL avatar")

            @validator('full_name')
            def validate_full_name(cls, v):
                if v is not None and not v.strip():
                    raise ValueError('Họ và tên không được để trống')
                return v.strip() if v else v

        return UpdateUserSchema

    @staticmethod
    def get_change_password_schema():
        """Schema cho changing password"""
        class ChangePasswordSchema(BaseModel):
            current_password: str = Field(..., min_length=1, description="Mật khẩu hiện tại")
            new_password: str = Field(..., min_length=8, max_length=100, description="Mật khẩu mới")

            @validator('new_password')
            def validate_password(cls, v):
                if not re.search(r'[A-Z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ hoa')
                if not re.search(r'[a-z]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ thường')
                if not re.search(r'[0-9]', v):
                    raise ValueError('Mật khẩu phải chứa ít nhất 1 chữ số')
                return v

        return ChangePasswordSchema

    @staticmethod
    def get_places_query_schema():
        """Schema cho places query parameters"""
        class PlacesQuerySchema(BaseModel):
            keyword: Optional[str] = Field(None, description="Từ khóa tìm kiếm")
            district_id: Optional[int] = Field(None, ge=1, description="ID quận/huyện")
            category_id: Optional[int] = Field(None, ge=1, description="ID danh mục")
            page: Optional[int] = Field(1, ge=1, description="Số trang")
            limit: Optional[int] = Field(10, ge=1, le=100, description="Số items mỗi trang")

        return PlacesQuerySchema

    @staticmethod
    def get_suggest_query_schema():
        """Schema cho suggest query parameters"""
        class SuggestQuerySchema(BaseModel):
            keyword: str = Field(..., min_length=1, max_length=100, description="Từ khóa gợi ý")

        return SuggestQuerySchema

    @staticmethod
    def get_add_favorite_schema():
        """Schema cho adding favorite place"""
        class AddFavoriteSchema(BaseModel):
            place_id: int = Field(..., ge=1, description="ID địa điểm")

        return AddFavoriteSchema

    @staticmethod
    def get_create_report_schema():
        """Schema cho creating report"""
        class CreateReportSchema(BaseModel):
            target_type: str = Field(..., regex=r'^(post|comment|user|place)$', description="Loại đối tượng báo cáo")
            target_id: int = Field(..., ge=1, description="ID đối tượng báo cáo")
            reason: str = Field(..., regex=r'^(spam|inappropriate|violence|copyright|other)$', description="Lý do báo cáo")
            description: Optional[str] = Field(None, max_length=500, description="Mô tả chi tiết")

        return CreateReportSchema

    @staticmethod
    def get_create_place_schema():
        """Schema cho creating place (admin)"""
        class CreatePlaceSchema(BaseModel):
            name: str = Field(..., min_length=2, max_length=200, description="Tên địa điểm")
            description: str = Field(..., min_length=10, max_length=2000, description="Mô tả địa điểm")
            address: str = Field(..., min_length=5, max_length=500, description="Địa chỉ")
            district_id: int = Field(..., ge=1, description="ID quận/huyện")
            category_id: int = Field(..., ge=1, description="ID danh mục")
            price_min: Optional[int] = Field(None, ge=0, description="Giá tối thiểu")
            price_max: Optional[int] = Field(None, ge=0, description="Giá tối đa")
            opening_hours: Optional[str] = Field(None, max_length=200, description="Giờ mở cửa")
            lat: float = Field(..., description="Vĩ độ")
            long: float = Field(..., description="Kinh độ")
            images: Optional[List[str]] = Field([], description="Danh sách URLs hình ảnh")

            @validator('name', 'description', 'address')
            def validate_required_fields(cls, v):
                if not v.strip():
                    raise ValueError('Không được để trống')
                return v.strip()

            @validator('images')
            def validate_images(cls, v):
                if v:
                    for img_url in v:
                        if not re.match(r'^https?://.+\.(jpg|jpeg|png|gif|webp)$', img_url):
                            raise ValueError('URL hình ảnh không hợp lệ')
                return v

        return CreatePlaceSchema

    @staticmethod
    def get_user_id_schema():
        """Schema cho user ID parameter"""
        class UserIdSchema(BaseModel):
            user_id: int = Field(..., ge=1, description="ID người dùng")

        return UserIdSchema

    @staticmethod
    def get_update_user_status_schema():
        """Schema cho updating user status (admin)"""
        class UpdateUserStatusSchema(BaseModel):
            status: str = Field(..., regex=r'^(active|blocked|suspended)$', description="Trạng thái người dùng")
            reason: Optional[str] = Field(None, max_length=500, description="Lý do thay đổi")

        return UpdateUserStatusSchema

    def get_stats(self) -> Dict[str, int]:
        """Lấy thống kê validation"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset thống kê validation"""
        self.stats = {
            "total_requests": 0,
            "validation_errors": 0,
            "validation_passed": 0,
        }


# Decorators cho manual validation

def validate_body(schema: Type[BaseModel]):
    """
    Decorator để validate request body

    Usage:
        @validate_body(UserCreateSchema)
        async def create_user(request: Request):
            body = await request.json()
            validated_data = UserCreateSchema.parse_obj(body)
            return {"message": "Success"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                try:
                    body_data = await request.json()
                    schema.parse_obj(body_data)
                except ValidationError as e:
                    raise ValidationException("VALIDATION_003", "Validation failed", e.errors())

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_query(schema: Type[BaseModel]):
    """Decorator để validate query parameters"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                try:
                    query_data = dict(request.query_params)
                    if query_data:
                        schema.parse_obj(query_data)
                except ValidationError as e:
                    raise ValidationException("VALIDATION_004", "Query validation failed", e.errors())

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Factory function
def create_validation_middleware(**kwargs):
    """
    Factory function để tạo ValidationMiddleware instance

    Args:
        **kwargs: Additional arguments cho ValidationMiddleware

    Returns:
        ValidationMiddleware instance
    """
    return lambda app: ValidationMiddleware(app, **kwargs)