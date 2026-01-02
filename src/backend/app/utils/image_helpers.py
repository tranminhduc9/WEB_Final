"""
Image Helper Functions - Simplified API for image URL handling

Tất cả xử lý ảnh được tập trung ở đây. API chỉ cần gọi 1 hàm là có kết quả.

Được sử dụng bởi: places.py, posts.py, chatbot.py, users.py
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
import uuid
import shutil
from pathlib import Path
import logging

# Import centralized image configuration
from config.image_config import (
    get_uploads_base_url,
    get_image_url,
    get_place_image_url,
    build_image_url_from_db,
    ImageFolder
)

logger = logging.getLogger(__name__)


async def save_upload_file(
    file: UploadFile, 
    folder: str = "misc",
    upload_type: str = "generic",
    entity_id: Optional[str] = None
) -> dict:
    """
    Save uploaded file to the configured uploads directory.
    
    Returns both relative path (for database storage) and full URL (for API response).
    This matches the pattern used by build_image_url_from_db() for reading images.
    
    Args:
        file: The uploaded file object
        folder: Subfolder name (default: "misc")
        upload_type: Type of upload - "place", "avatar", "post", or "generic"
        entity_id: ID of the entity (place_id, user_id, post_id) - required for typed uploads
        
    Returns:
        Dict with:
            - relative_path: Relative path for database (e.g., "places/place_1_0.jpg")
            - url: Full URL for API response (e.g., "http://.../uploads/places/place_1_0.jpg")
            - filename: Just the filename
    """
    try:
        # Determine uploads directory path using ABSOLUTE path
        # This ensures it works regardless of where the script is run from
        # Convert __file__ to absolute path first, then navigate to src/static/uploads
        current_file = Path(__file__).resolve()
        # src/backend/app/utils/image_helpers.py -> src/backend/app/utils
        # -> src/backend/app -> src/backend -> src -> src/static -> src/static/uploads
        src_dir = current_file.parent.parent.parent.parent  # Go up to src/backend -> src
        base_upload_dir = src_dir / "static" / "uploads"
        
        # Auto-determine folder based on upload_type
        # This ensures images are saved to the correct subfolder even if folder param is wrong
        type_to_folder = {
            "place": "places",
            "avatar": "avatars", 
            "post": "posts"
        }
        if upload_type in type_to_folder:
            folder = type_to_folder[upload_type]
        
        # Create subfolder
        target_dir = base_upload_dir / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Get file extension
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'


        
        # Generate filename based on upload type
        if upload_type == "place" and entity_id:
            # Count existing images for this place
            existing = list(target_dir.glob(f"place_{entity_id}_*.{ext}"))
            index = len(existing)
            filename = f"place_{entity_id}_{index}.{ext}"
            
        elif upload_type == "avatar" and entity_id:
            # Delete old avatar if exists (any extension)
            old_avatars = list(target_dir.glob(f"avatar_{entity_id}.*"))
            for old_avatar in old_avatars:
                old_avatar.unlink()
            
            # Simple avatar naming: avatar_{user_id}.{ext}
            # This matches the reading logic in image_config.py
            filename = f"avatar_{entity_id}.{ext}"
            
        elif upload_type == "post" and entity_id:
            # Count existing images for this post
            existing = list(target_dir.glob(f"post_{entity_id}_*.{ext}"))
            index = len(existing)
            filename = f"post_{entity_id}_{index}.{ext}"
            
        else:
            # Generic upload - use UUID
            filename = f"{uuid.uuid4()}.{ext}"
        
        filepath = target_dir / filename
        
        # Save file
        # Note: Using await file.read() is safer for async contexts
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # Build paths to match database format
        # Database stores: /static/uploads/places/place_1_0.jpg
        # NOT just: places/place_1_0.jpg
        relative_path = f"/static/uploads/{folder}/{filename}"  # For database
        full_url = get_uploads_base_url() + "/" + folder + "/" + filename  # For API response
        
        logger.info(f"Uploaded {upload_type} file: {relative_path}")
        
        return {
            "relative_path": relative_path,
            "url": full_url,
            "filename": filename
        }
            
    except Exception as e:
        logger.error(f"Error saving upload file: {str(e)}")
        raise e




async def save_place_image(file: UploadFile, place_id: int) -> dict:
    """
    Convenience wrapper for uploading place images.
    
    Args:
        file: The uploaded file
        place_id: ID of the place
        
    Returns:
        Dict with relative_path, url, and filename
    """
    return await save_upload_file(file, "places", "place", str(place_id))


async def save_avatar_image(file: UploadFile, user_id: int) -> dict:
    """
    Convenience wrapper for uploading avatar images.
    
    Args:
        file: The uploaded file
        user_id: ID of the user
        
    Returns:
        Dict with relative_path, url, and filename
    """
    return await save_upload_file(file, "avatars", "avatar", str(user_id))


async def save_post_image(file: UploadFile, post_id: str) -> dict:
    """
    Convenience wrapper for uploading post images.
    
    Args:
        file: The uploaded file
        post_id: MongoDB ObjectId of the post
        
    Returns:
        Dict with relative_path, url, and filename
    """
    return await save_upload_file(file, "posts", "post", post_id)


def get_main_image_url(place_id: int, db: Session = None) -> str:
    """
    Lấy URL ảnh chính của địa điểm.
    API chỉ cần gọi hàm này, không cần xử lý gì thêm.
    
    Args:
        place_id: ID của địa điểm
        db: Database session
        
    Returns:
        Full URL đến ảnh (sử dụng UPLOADS_BASE_URL từ .env)
    """
    import os
    from config.database import PlaceImage
    
    # 1. Tìm trong database
    if db:
        # Try main image first
        main_image = db.query(PlaceImage).filter(
            PlaceImage.place_id == place_id,
            PlaceImage.is_main == True
        ).first()
        
        if main_image and main_image.image_url:
            return build_image_url_from_db(main_image.image_url)
        
        # Lấy ảnh đầu tiên nếu không có ảnh chính
        first_image = db.query(PlaceImage).filter(
            PlaceImage.place_id == place_id
        ).first()
        
        if first_image and first_image.image_url:
            return build_image_url_from_db(first_image.image_url)
    
    # 2. Tìm trong local uploads folder using absolute path
    current_file_path = Path(__file__).resolve()
    src_dir = current_file_path.parent.parent.parent.parent  # src/backend -> src
    uploads_dir = src_dir / "static" / "uploads" / "places"
    
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        local_file = f"place_{place_id}_0.{ext}"
        local_path = uploads_dir / local_file
        if local_path.exists():
            return get_image_url(ImageFolder.PLACES, local_file)
    
    # 3. Return default URL
    return get_place_image_url(place_id, 0, "jpg")



def get_all_place_images(place_id: int, db: Session) -> List[str]:
    """
    Lấy tất cả ảnh của một địa điểm.
    API chỉ cần gọi hàm này, không cần xử lý gì thêm.
    
    Args:
        place_id: ID của địa điểm
        db: Database session
        
    Returns:
        List of full URLs to images
    """
    from config.database import PlaceImage
    
    images = []
    
    image_records = db.query(PlaceImage).filter(
        PlaceImage.place_id == place_id
    ).order_by(PlaceImage.is_main.desc(), PlaceImage.id.asc()).all()
    
    for img in image_records:
        if img.image_url:
            images.append(build_image_url_from_db(img.image_url))
    
    # Fallback to main image if no images found
    if not images:
        images.append(get_main_image_url(place_id, db))
    
    return images


def normalize_image_url(url: str) -> str:
    """
    Normalize any image URL/path to full URL.
    API chỉ cần gọi hàm này cho bất kỳ URL nào.
    
    Args:
        url: Image URL or relative path
        
    Returns:
        Full URL
    """
    return build_image_url_from_db(url)


def normalize_image_list(images: List[str]) -> List[str]:
    """
    Normalize a list of image URLs/paths to full URLs.
    API chỉ cần gọi hàm này cho list ảnh.
    
    Args:
        images: List of image URLs or relative paths
        
    Returns:
        List of full URLs
    """
    if not images:
        return []
    return [build_image_url_from_db(img) for img in images if img]


def get_avatar_url(avatar_path: str = None, user_id: int = None, full_name: str = None) -> str:
    """
    Lấy URL avatar của user.
    API chỉ cần gọi hàm này.
    
    Args:
        avatar_path: Avatar path/URL from database
        user_id: User ID (optional, for fallback)
        full_name: User's full name (optional, for generating personalized avatar)
        
    Returns:
        Full URL to avatar (fallback to default if no avatar)
    """
    # Default avatar URL - using a stable, reliable placeholder service
    DEFAULT_AVATAR = "https://ui-avatars.com/api/?name=User&background=F88622&color=fff&size=150&bold=true"
    
    if avatar_path:
        return build_image_url_from_db(avatar_path)
    
    # Generate personalized default avatar using first letter of name
    if full_name:
        # URL encode the name for safe URL usage
        import urllib.parse
        # Use first 2 characters or initials for better display
        name_parts = full_name.strip().split()
        if len(name_parts) >= 2:
            # Get initials: "Nguyen Van A" -> "NA"
            initials = name_parts[0][0] + name_parts[-1][0]
        else:
            # Single name: take first 2 chars
            initials = full_name[:2] if len(full_name) >= 2 else full_name
        encoded_name = urllib.parse.quote(initials.upper())
        return f"https://ui-avatars.com/api/?name={encoded_name}&background=F88622&color=fff&size=150&bold=true"
    
    # Fallback to user_id if no name available
    if user_id:
        return f"https://ui-avatars.com/api/?name=U{user_id}&background=F88622&color=fff&size=150&bold=true"
    
    return DEFAULT_AVATAR


def get_banned_user_avatar() -> str:
    """
    Trả về avatar cho tài khoản bị ban.
    Hiển thị dấu chấm than (!) với nền đỏ.
    """
    # Exclamation mark with red background
    return "https://ui-avatars.com/api/?name=!&background=DC3545&color=fff&size=150&bold=true"


def get_deleted_user_avatar() -> str:
    """
    Trả về avatar cho tài khoản đã xóa.
    Hiển thị ký tự X với nền xám.
    """
    # X mark with gray background
    return "https://ui-avatars.com/api/?name=X&background=6C757D&color=fff&size=150&bold=true"


def get_post_images(post: dict) -> List[str]:
    """
    Lấy và normalize tất cả ảnh của một post.
    API chỉ cần gọi hàm này.
    
    Args:
        post: Post document từ MongoDB
        
    Returns:
        List of full URLs
    """
    images = post.get("images", [])
    return normalize_image_list(images)


def format_place_compact_images(place_id: int, db: Session, main_image_url: str = None) -> str:
    """
    Lấy ảnh cho PlaceCompact format.
    Nếu đã có main_image_url thì normalize, không thì query database.
    
    Args:
        place_id: Place ID
        db: Database session
        main_image_url: Existing main image URL (optional)
        
    Returns:
        Full URL to main image
    """
    if main_image_url:
        return build_image_url_from_db(main_image_url)
    return get_main_image_url(place_id, db)
