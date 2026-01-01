"""
Place Helper Functions - Shared utilities for place data handling

Được sử dụng bởi: posts.py, chatbot.py
"""

import os
from typing import Optional, Dict
from sqlalchemy.orm import Session


def get_place_compact(place_id: int, db: Session) -> Optional[Dict]:
    """
    Lấy thông tin place compact theo Swagger PlaceCompact schema.
    
    PlaceCompact fields:
    - id, name, district_id, place_type_id
    - rating_average, price_min, price_max, main_image_url
    
    Args:
        place_id: ID của địa điểm (có thể là int hoặc string)
        db: Database session
        
    Returns:
        Dict chứa PlaceCompact data hoặc None nếu không tìm thấy
    """
    # Convert place_id to int if it's a string (MongoDB may store as string)
    if isinstance(place_id, str):
        try:
            place_id = int(place_id)
        except ValueError:
            return None
    
    if not place_id:
        return None
    
    # Import here to avoid circular imports
    from config.database import Place
    from app.utils.image_helpers import get_main_image_url
    
    place = db.query(Place).filter(Place.id == place_id).first()
    if place:
        # Auto-swap price nếu bị đảo ngược trong database
        price_min = float(place.price_min) if place.price_min else 0
        price_max = float(place.price_max) if place.price_max else 0
        # Swap khi price_min > price_max (dữ liệu bị lưu ngược)
        if price_min > price_max:
            price_min, price_max = price_max, price_min
        
        return {
            "id": place.id,
            "name": place.name,
            "district_id": place.district_id,
            "place_type_id": place.place_type_id,
            "rating_average": float(place.rating_average) if place.rating_average else 0,
            "rating_count": place.rating_count or 0,
            "price_min": price_min,
            "price_max": price_max,
            "main_image_url": get_main_image_url(place_id, db)
        }
    return None


def get_user_compact(user_id: int, db: Session) -> Optional[Dict]:
    """
    Lấy thông tin user compact theo Swagger UserCompact schema.
    
    UserCompact fields:
    - id, full_name, avatar_url, role_id, is_banned
    
    Nếu user bị xóa: full_name = "Tài khoản bị xóa"
    Nếu user bị ban: full_name = "Tài khoản bị ban"
    
    Args:
        user_id: ID của user
        db: Database session
        
    Returns:
        Dict chứa UserCompact data hoặc None nếu không tìm thấy
    """
    from config.database import User
    from app.utils.image_helpers import get_avatar_url
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Check if user is deleted first (higher priority)
        if user.deleted_at is not None:
            from app.utils.image_helpers import get_deleted_user_avatar
            return {
                "id": user.id,
                "full_name": "Tài khoản bị xóa",
                "avatar_url": get_deleted_user_avatar(),  # X mark with gray background
                "role_id": user.role_id,
                "is_banned": True,
                "status": "deleted"
            }
        
        # Check if user is banned
        if not user.is_active:
            from app.utils.image_helpers import get_banned_user_avatar
            return {
                "id": user.id,
                "full_name": "Tài khoản bị ban",
                "avatar_url": get_banned_user_avatar(),  # ! mark with red background
                "role_id": user.role_id,
                "is_banned": True,
                "status": "banned"
            }
        
        return {
            "id": user.id,
            "full_name": user.full_name,
            "avatar_url": get_avatar_url(user.avatar_url, user.id, user.full_name),
            "role_id": user.role_id,
            "is_banned": False,
            "status": "active"
        }
    return None

