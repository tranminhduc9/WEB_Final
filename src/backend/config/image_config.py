"""
Image Configuration Module

Centralized configuration for image/upload URLs.
Supports both local development and cloud deployment (AWS S3, CloudFront).

Usage:
    from config.image_config import get_image_url, ImageFolder
    
    # Get full URL for a place image
    url = get_image_url(ImageFolder.PLACES, "place_1_0.jpg")
    # Returns: http://127.0.0.1:8080/static/uploads/places/place_1_0.jpg (local)
    # Or: https://bucket.s3.amazonaws.com/static/uploads/places/place_1_0.jpg (AWS)
"""

import os
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageFolder(str, Enum):
    """Available image folders"""
    PLACES = "places"
    AVATARS = "avatars"
    POSTS = "posts"


def is_s3_enabled() -> bool:
    """
    Check if S3 storage is enabled via environment variable.
    
    Returns:
        True if USE_S3=true, False otherwise
    """
    return os.getenv("USE_S3", "false").lower() == "true"


def get_s3_config() -> dict:
    """
    Get S3 configuration from environment variables.
    
    Returns:
        Dict with AWS S3 configuration
    """
    return {
        "access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
        "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        "bucket": os.getenv("AWS_S3_BUCKET", ""),
        "region": os.getenv("AWS_S3_REGION", "ap-southeast-2"),
    }


def get_uploads_base_url() -> str:
    """
    Get base URL for uploads from environment.
    
    Returns:
        Base URL like "http://127.0.0.1:8080/static/uploads" or 
        "https://bucket.s3.amazonaws.com/static/uploads"
    """
    # Get from environment, with default for local development
    base_url = os.getenv("UPLOADS_BASE_URL", "http://127.0.0.1:8080/static/uploads")
    
    # Sanitize: Handle case where .env has duplicate value like UPLOADS_BASE_URL=UPLOADS_BASE_URL=http://...
    # This can happen if user accidentally types it wrong
    if base_url and not base_url.startswith('http'):
        # Try to extract the actual URL from malformed value
        if 'http://' in base_url:
            base_url = 'http://' + base_url.split('http://')[-1]
        elif 'https://' in base_url:
            base_url = 'https://' + base_url.split('https://')[-1]
        else:
            # Fallback to default
            logger.warning(f"Invalid UPLOADS_BASE_URL value: {base_url}, using default")
            base_url = "http://127.0.0.1:8080/static/uploads"
    
    return base_url.rstrip('/')


def get_default_uploads_base_url() -> str:
    """
    Get the default base URL for S3 uploads based on bucket and region.
    Falls back to UPLOADS_BASE_URL if set.
    
    Returns:
        S3 URL like "https://bucket.s3.region.amazonaws.com/static/uploads"
    """
    if is_s3_enabled():
        config = get_s3_config()
        bucket = config["bucket"]
        region = config["region"]
        if bucket:
            return f"https://{bucket}.s3.{region}.amazonaws.com/static/uploads"
    
    return get_uploads_base_url()


def get_image_url(folder: ImageFolder, filename: str) -> str:
    """
    Generate full URL for an image.
    
    Args:
        folder: ImageFolder enum (PLACES, AVATARS, POSTS)
        filename: Image filename (e.g., "place_1_0.jpg")
    
    Returns:
        Full URL to the image
        
    Example:
        get_image_url(ImageFolder.PLACES, "place_1_0.jpg")
        # Local: http://127.0.0.1:8080/static/uploads/places/place_1_0.jpg
        # AWS:   https://bucket.s3.amazonaws.com/static/uploads/places/place_1_0.jpg
    """
    if not filename:
        return get_placeholder_url(folder)
    
    base_url = get_uploads_base_url()
    return f"{base_url}/{folder.value}/{filename}"


def get_place_image_url(place_id: int, image_index: int = 0, extension: str = "jpg") -> str:
    """
    Generate URL for a place image using naming convention.
    
    Args:
        place_id: Place ID
        image_index: Image index (0 = main image)
        extension: File extension (jpg, png, etc.)
    
    Returns:
        Full URL like http://base/places/place_1_0.jpg
    """
    filename = f"place_{place_id}_{image_index}.{extension}"
    return get_image_url(ImageFolder.PLACES, filename)


def get_avatar_url(user_id: int, extension: str = "jpg") -> str:
    """
    Generate URL for a user avatar.
    
    Args:
        user_id: User ID
        extension: File extension
    
    Returns:
        Full URL like http://base/avatars/avatar_1.jpg
    """
    filename = f"avatar_{user_id}.{extension}"
    return get_image_url(ImageFolder.AVATARS, filename)


def get_post_image_url(post_id: str, image_index: int = 0, extension: str = "jpg") -> str:
    """
    Generate URL for a post image.
    
    Args:
        post_id: Post ID (MongoDB ObjectId as string)
        image_index: Image index
        extension: File extension
    
    Returns:
        Full URL like http://base/posts/post_abc123_0.jpg
    """
    filename = f"post_{post_id}_{image_index}.{extension}"
    return get_image_url(ImageFolder.POSTS, filename)


def get_placeholder_url(folder: ImageFolder = ImageFolder.PLACES) -> str:
    """
    Get placeholder image URL when no image is available.
    Uses external placeholder service for reliability.
    
    Args:
        folder: ImageFolder to get placeholder for
    
    Returns:
        Placeholder URL
    """
    # Use external placeholder service for reliability
    placeholders = {
        ImageFolder.PLACES: "https://placehold.co/400x300/F88622/white?text=No+Image",
        ImageFolder.AVATARS: "https://ui-avatars.com/api/?name=User&background=F88622&color=fff&size=150&bold=true",
        ImageFolder.POSTS: "https://placehold.co/600x400/F88622/white?text=No+Image",
    }
    return placeholders.get(folder, placeholders[ImageFolder.PLACES])


def build_image_url_from_db(db_path: str) -> str:
    """
    Build full URL from database-stored path.
    
    Database stores path as: folder/filename (e.g., "avatars/avatar_52.png")
    This function combines UPLOADS_BASE_URL + path to create full URL.
    
    Args:
        db_path: Path stored in database (format: folder/filename)
    
    Returns:
        Full URL (e.g., "http://127.0.0.1:8080/static/uploads/avatars/avatar_52.png")
    """
    if not db_path:
        return get_placeholder_url()
    
    # Already a full URL (http:// or https://)
    if db_path.startswith('http'):
        return db_path
    
    base_url = get_uploads_base_url()
    
    # Clean path - remove leading slash if present
    clean_path = db_path.lstrip('/')
    
    return f"{base_url}/{clean_path}"
