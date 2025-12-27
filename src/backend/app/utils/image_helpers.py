"""
Image Helper Functions - Shared utilities for image URL handling

Tập trung các hàm xử lý ảnh để tránh code duplication.
Được sử dụng bởi: places.py, posts.py, chatbot.py, users.py
"""

import os
from typing import Optional
from sqlalchemy.orm import Session


def get_main_image_url(place_id: int, db: Session = None) -> str:
    """
    Lấy ảnh chính của địa điểm.
    
    Priority:
    1. Database place_images table (is_main=True)
    2. Local uploads folder: /uploads/places/place_{id}_0.{ext}
    3. Default placeholder
    
    Args:
        place_id: ID của địa điểm
        db: Database session (optional, để query PlaceImage)
        
    Returns:
        Full URL đến ảnh (http://localhost:8080/uploads/places/...)
    """
    # Import here to avoid circular imports
    from config.database import PlaceImage
    
    # Get base URL for static files
    backend_host = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port = os.getenv("BACKEND_PORT", "8080")
    base_url = f"http://{backend_host}:{backend_port}"
    
    # 1. Tìm trong database
    if db:
        main_image = db.query(PlaceImage).filter(
            PlaceImage.place_id == place_id,
            PlaceImage.is_main == True
        ).first()
        
        if main_image and main_image.image_url:
            # Nếu đã là full URL thì trả về luôn
            if main_image.image_url.startswith('http'):
                return main_image.image_url
            return f"{base_url}{main_image.image_url}"
        
        # Lấy ảnh đầu tiên nếu không có ảnh chính
        first_image = db.query(PlaceImage).filter(
            PlaceImage.place_id == place_id
        ).first()
        
        if first_image and first_image.image_url:
            if first_image.image_url.startswith('http'):
                return first_image.image_url
            return f"{base_url}{first_image.image_url}"
    
    # 2. Tìm trong local uploads folder
    # Path: src/backend/app/utils -> src/uploads/places
    uploads_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "..", "uploads", "places"
    )
    
    # Thử các extension phổ biến
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        local_file = f"place_{place_id}_0.{ext}"
        local_path = os.path.join(uploads_dir, local_file)
        if os.path.exists(local_path):
            return f"{base_url}/uploads/places/{local_file}"
    
    # 3. Default placeholder
    return f"{base_url}/uploads/places/place_{place_id}_0.jpg"
