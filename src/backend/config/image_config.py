"""
Image Configuration Module

Centralized configuration for image/upload URLs.
Supports both local development and cloud deployment (AWS S3, CloudFront).

Usage:
    from config.image_config import get_image_url, ImageFolder
    
    # Get full URL for a place image
    url = get_image_url(ImageFolder.PLACES, "place_1_0.jpg")
    # Returns: http://127.0.0.1:8080/static/uploads/places/place_1_0.jpg (local)
    # Or: https://bucket.s3.amazonaws.com/uploads/places/place_1_0.jpg (AWS)
"""

import os
from enum import Enum
from typing import Optional


class ImageFolder(str, Enum):
    """Available image folders"""
    PLACES = "places"
    AVATARS = "avatars"
    POSTS = "posts"


def get_uploads_base_url() -> str:
    """
    Get base URL for uploads from environment.
    
    Returns:
        Base URL like "http://127.0.0.1:8080/static/uploads" or 
        "https://bucket.s3.amazonaws.com/uploads"
    """
    # Get from environment, with default for local development
    base_url = os.getenv("UPLOADS_BASE_URL", "http://127.0.0.1:8080/static/uploads")
    return base_url.rstrip('/')


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
        # AWS:   https://bucket.s3.amazonaws.com/uploads/places/place_1_0.jpg
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
    
    Args:
        folder: ImageFolder to get placeholder for
    
    Returns:
        Placeholder URL
    """
    base_url = get_uploads_base_url()
    return f"{base_url}/{folder.value}/placeholder.jpg"


def build_image_url_from_db(db_path: str) -> str:
    """
    Build full URL from database-stored path.
    
    The database may store relative paths like:
    - /static/uploads/places/place_1_0.jpg
    - places/place_1_0.jpg
    - place_1_0.jpg (just filename)
    
    This function converts them to full URLs using UPLOADS_BASE_URL.
    
    Args:
        db_path: Path stored in database
    
    Returns:
        Full URL
    """
    if not db_path:
        return get_placeholder_url()
    
    # Already a full URL (http:// or https://)
    if db_path.startswith('http'):
        return db_path
    
    base_url = get_uploads_base_url()
    
    # Remove any leading prefixes to get clean path
    clean_path = db_path
    
    # Strip common prefixes
    prefixes_to_remove = ['/static/uploads/', '/uploads/', 'static/uploads/', 'uploads/']
    for prefix in prefixes_to_remove:
        if clean_path.startswith(prefix):
            clean_path = clean_path[len(prefix):]
            break
    
    # Remove leading slash if present
    clean_path = clean_path.lstrip('/')
    
    return f"{base_url}/{clean_path}"
