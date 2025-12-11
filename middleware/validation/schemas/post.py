"""
Post validation schemas.

Pydantic schemas for validating post-related requests.
Implementation following Task #4 validation requirements.
"""

import re
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class CreatePostSchema(BaseModel):
    """
    Schema for creating a new post.

    Rules:
    - title: 10-200 characters, required
    - content: not empty, required
    - cover_image: valid URL, optional
    - related_place_id: integer, optional
    - tags: array of strings, max 5 items, optional
    """

    title: str = Field(..., min_length=10, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post content")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    related_place_id: Optional[int] = Field(None, description="Related place ID")
    tags: Optional[List[str]] = Field([], description="Post tags")

    @validator('title')
    def validate_title(cls, v):
        """Validate title is not just whitespace."""
        if not v.strip():
            raise ValueError('Tiêu đề không được để trống')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        """Validate content is not just whitespace."""
        if not v.strip():
            raise ValueError('Nội dung không được để trống')
        return v.strip()

    @validator('cover_image')
    def validate_cover_image(cls, v):
        """Validate cover image URL if provided."""
        if v is None:
            return v

        # Basic URL validation
        url_regex = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if not re.match(url_regex, v):
            raise ValueError('URL hình ảnh không hợp lệ')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags array."""
        if v is None:
            return []

        # Check max 5 tags
        if len(v) > 5:
            raise ValueError('Tối đa 5 thẻ được phép')

        # Validate each tag
        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('Thẻ phải là chuỗi ký tự')

            tag = tag.strip()
            if not tag:
                continue

            if len(tag) > 50:
                raise ValueError('Thẻ không được vượt quá 50 ký tự')

            # Remove duplicate tags
            if tag not in validated_tags:
                validated_tags.append(tag)

        return validated_tags

    @validator('related_place_id')
    def validate_related_place_id(cls, v):
        """Validate place ID if provided."""
        if v is None:
            return v

        if not isinstance(v, int) or v <= 0:
            raise ValueError('ID địa điểm phải là số nguyên dương')
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Hà Nội - Thủ đô ngàn năm văn hiến",
                "content": "Hà Nội là thủ đô của Việt Nam với lịch sử lâu đời...",
                "cover_image": "https://example.com/hanoi-cover.jpg",
                "related_place_id": 1,
                "tags": ["Hà Nội", "Du lịch", "Văn hóa"]
            }
        }


class UpdatePostSchema(BaseModel):
    """
    Schema for updating an existing post.

    All fields are optional for partial updates.
    """

    title: Optional[str] = Field(None, min_length=10, max_length=200, description="Post title")
    content: Optional[str] = Field(None, min_length=1, description="Post content")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    related_place_id: Optional[int] = Field(None, description="Related place ID")
    tags: Optional[List[str]] = Field(None, description="Post tags")

    @validator('title')
    def validate_title(cls, v):
        """Validate title if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError('Tiêu đề không được để trống')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        """Validate content if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError('Nội dung không được để trống')
        return v.strip()

    @validator('cover_image')
    def validate_cover_image(cls, v):
        """Validate cover image URL if provided."""
        if v is None:
            return v

        # Basic URL validation
        url_regex = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        if not re.match(url_regex, v):
            raise ValueError('URL hình ảnh không hợp lệ')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags array if provided."""
        if v is None:
            return None

        # Check max 5 tags
        if len(v) > 5:
            raise ValueError('Tối đa 5 thẻ được phép')

        # Validate each tag
        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('Thẻ phải là chuỗi ký tự')

            tag = tag.strip()
            if not tag:
                continue

            if len(tag) > 50:
                raise ValueError('Thẻ không được vượt quá 50 ký tự')

            # Remove duplicate tags
            if tag not in validated_tags:
                validated_tags.append(tag)

        return validated_tags

    @validator('related_place_id')
    def validate_related_place_id(cls, v):
        """Validate place ID if provided."""
        if v is None:
            return v

        if not isinstance(v, int) or v <= 0:
            raise ValueError('ID địa điểm phải là số nguyên dương')
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Hà Nội - Thủ đô ngàn năm văn hiến (Updated)",
                "content": "Nội dung đã được cập nhật...",
                "tags": ["Hà Nội", "Du lịch", "Văn hóa", "Lịch sử"]
            }
        }


class CommentSchema(BaseModel):
    """
    Schema for creating comments on posts.
    """

    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")
    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")

    @validator('content')
    def validate_content(cls, v):
        """Validate comment content."""
        if not v.strip():
            raise ValueError('Nội dung bình luận không được để trống')
        return v.strip()

    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent comment ID if provided."""
        if v is None:
            return v

        if not isinstance(v, int) or v <= 0:
            raise ValueError('ID bình luận cha phải là số nguyên dương')
        return v

    class Config:
        schema_extra = {
            "example": {
                "content": "Bài viết rất hay và hữu ích!",
                "parent_id": None
            }
        }


class SearchPostSchema(BaseModel):
    """
    Schema for searching posts with filters.
    """

    keyword: Optional[str] = Field(None, description="Search keyword")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    place_id: Optional[int] = Field(None, description="Filter by place ID")
    author_id: Optional[int] = Field(None, description="Filter by author ID")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order")

    @validator('keyword')
    def validate_keyword(cls, v):
        """Validate search keyword."""
        if v is None:
            return v

        keyword = v.strip()
        if len(keyword) < 2:
            raise ValueError('Từ khóa tìm kiếm phải có ít nhất 2 ký tự')
        if len(keyword) > 100:
            raise ValueError('Từ khóa tìm kiếm không được vượt quá 100 ký tự')
        return keyword

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags filter."""
        if v is None:
            return v

        if len(v) > 10:
            raise ValueError('Tối đa 10 thẻ được phép lọc')

        validated_tags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                validated_tags.append(tag.strip())

        return validated_tags

    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Validate sort field."""
        allowed_fields = ['created_at', 'updated_at', 'title', 'views', 'likes']
        if v not in allowed_fields:
            raise ValueError(f'Trường sắp xếp không hợp lệ. Cho phép: {", ".join(allowed_fields)}')
        return v

    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ['asc', 'desc']:
            raise ValueError('Thứ tự sắp xếp phải là "asc" hoặc "desc"')
        return v

    class Config:
        schema_extra = {
            "example": {
                "keyword": "Hà Nội",
                "tags": ["Du lịch", "Văn hóa"],
                "page": 1,
                "limit": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }