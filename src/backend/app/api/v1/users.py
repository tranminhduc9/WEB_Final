"""
Users API Routes

Module này định nghĩa các API endpoints cho Users bao gồm:
- GET /users/me - Lấy thông tin profile
- PUT /users/me - Cập nhật profile
- PUT /users/change-password - Đổi mật khẩu
- DELETE /users/me/favorites/places/{id} - Xóa địa điểm yêu thích

Swagger v1.0.5 Compatible
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import logging

from config.database import get_db, User, UserPlaceFavorite, UserPostFavorite, Place
from middleware.auth import get_current_user
from middleware.response import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


# ==================== REQUEST SCHEMAS ====================

class UpdateProfileRequest(BaseModel):
    """Schema cập nhật profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class ChangePasswordRequest(BaseModel):
    """Schema đổi mật khẩu"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


# ==================== ENDPOINTS ====================

@router.get("/me", summary="Get Profile")
async def get_user_profile(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin profile của user hiện tại
    
    Returns:
        - user: Thông tin user
        - stats: Thống kê (số bài viết, etc.)
        - recent_favorites: Địa điểm yêu thích gần đây
        - recent_posts: Bài viết gần đây
    """
    try:
        user_id = current_user.get("user_id")
        
        # Lấy user từ database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Lấy favorites
        favorites = db.query(UserPlaceFavorite).filter(
            UserPlaceFavorite.user_id == user_id
        ).order_by(UserPlaceFavorite.created_at.desc()).limit(5).all()
        
        recent_favorites = []
        for fav in favorites:
            place = db.query(Place).filter(Place.id == fav.place_id).first()
            if place:
                recent_favorites.append({
                    "id": place.id,
                    "name": place.name,
                    "district_id": place.district_id,
                    "place_type_id": place.place_type_id,
                    "rating_average": float(place.rating_average) if place.rating_average else 0,
                    "price_min": float(place.price_min) if place.price_min else 0,
                    "price_max": float(place.price_max) if place.price_max else 0,
                    "main_image_url": None  # TODO: Get from place_images
                })
        
        # TODO: Get posts from MongoDB
        recent_posts = []
        
        # Stats
        stats = {
            "posts_count": 0,  # TODO: Count from MongoDB
            "favorites_count": db.query(UserPlaceFavorite).filter(
                UserPlaceFavorite.user_id == user_id
            ).count()
        }
        
        return success_response(
            message="Lấy thông tin profile thành công",
            data={
                "user": {
                    # Swagger UserDetailResponse.data.user: id, full_name, email, bio, reputation_score
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "bio": user.bio,
                    "reputation_score": user.reputation_score
                },
                "stats": stats,
                "recent_favorites": recent_favorites,
                "recent_posts": recent_posts
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return error_response(
            message="Lỗi lấy thông tin profile",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.put("/me", summary="Update Profile")
async def update_user_profile(
    request: Request,
    update_data: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin profile
    
    Args:
        full_name: Tên đầy đủ (optional)
        bio: Tiểu sử (optional)
        avatar_url: URL ảnh đại diện (optional)
    """
    try:
        user_id = current_user.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Update fields
        if update_data.full_name is not None:
            user.full_name = update_data.full_name
        if update_data.bio is not None:
            user.bio = update_data.bio
        if update_data.avatar_url is not None:
            user.avatar_url = update_data.avatar_url
        
        db.commit()
        db.refresh(user)
        
        return success_response(
            message="Cập nhật profile thành công",
            data={
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "avatar_url": user.avatar_url,
                    "bio": user.bio,
                    "reputation_score": user.reputation_score
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        return error_response(
            message="Lỗi cập nhật profile",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.put("/change-password", summary="Change Password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đổi mật khẩu
    
    Args:
        current_password: Mật khẩu hiện tại
        new_password: Mật khẩu mới (tối thiểu 6 ký tự)
    """
    try:
        from middleware.auth import auth_middleware
        
        user_id = current_user.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Verify current password
        if not auth_middleware.verify_password(password_data.current_password, user.password_hash):
            return error_response(
                message="Mật khẩu hiện tại không đúng",
                error_code="INVALID_PASSWORD",
                status_code=400
            )
        
        # Hash and update new password
        user.password_hash = auth_middleware.hash_password(password_data.new_password)
        db.commit()
        
        return success_response(message="Đổi mật khẩu thành công")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password: {str(e)}")
        return error_response(
            message="Lỗi đổi mật khẩu",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/me/favorites/places/{place_id}", summary="Remove Favorite Place")
async def remove_favorite_place(
    request: Request,
    place_id: int = Path(..., description="ID địa điểm"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa địa điểm khỏi danh sách yêu thích
    """
    try:
        user_id = current_user.get("user_id")
        
        # Tìm favorite
        favorite = db.query(UserPlaceFavorite).filter(
            UserPlaceFavorite.user_id == user_id,
            UserPlaceFavorite.place_id == place_id
        ).first()
        
        if not favorite:
            return error_response(
                message="Địa điểm không nằm trong danh sách yêu thích",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        db.delete(favorite)
        db.commit()
        
        return success_response(message="Đã xóa khỏi danh sách yêu thích")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing favorite: {str(e)}")
        return error_response(
            message="Lỗi xóa địa điểm yêu thích",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF USERS ROUTES ====================
