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
        place_id: ID của địa điểm
        db: Database session
        
    Returns:
        Dict chứa PlaceCompact data hoặc None nếu không tìm thấy
    """
    # Import here to avoid circular imports
    from config.database import Place
    from app.utils.image_helpers import get_main_image_url
    
    place = db.query(Place).filter(Place.id == place_id).first()
    if place:
        # Auto-swap price nếu bị đảo ngược
        price_min = float(place.price_min) if place.price_min else 0
        price_max = float(place.price_max) if place.price_max else 0
        if price_min > price_max and price_max > 0:
            price_min, price_max = price_max, price_min
        
        return {
            "id": place.id,
            "name": place.name,
            "district_id": place.district_id,
            "place_type_id": place.place_type_id,
            "rating_average": float(place.rating_average) if place.rating_average else 0,
            "price_min": price_min,
            "price_max": price_max,
            "main_image_url": get_main_image_url(place_id, db)
        }
    return None


def get_user_compact(user_id: int, db: Session) -> Optional[Dict]:
    """
    Lấy thông tin user compact theo Swagger UserCompact schema.
    
    UserCompact fields:
    - id, full_name, avatar_url, role_id
    
    Args:
        user_id: ID của user
        db: Database session
        
    Returns:
        Dict chứa UserCompact data hoặc None nếu không tìm thấy
    """
    from config.database import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {
            "id": user.id,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "role_id": user.role_id
        }
    return None
