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

from config.database import get_db, User, UserPlaceFavorite, UserPostFavorite, Place, PlaceImage, District
from app.utils.image_helpers import get_main_image_url, normalize_image_list, get_avatar_url
from middleware.auth import get_current_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

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
        - user: Thông tin user (theo Swagger UserDetailResponse)
        - stats: Thống kê (số bài viết, etc.)
        - recent_favorites: Địa điểm yêu thích gần đây
        - recent_posts: Bài viết gần đây
    """
    try:
        await get_mongodb()  # Ensure MongoDB connection
        
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
                # Auto-swap nếu giá trị bị đảo ngược trong database
                price_min = float(place.price_min) if place.price_min else 0
                price_max = float(place.price_max) if place.price_max else 0
                # Swap khi price_min > price_max (dữ liệu bị lưu ngược)
                if price_min > price_max:
                    price_min, price_max = price_max, price_min
                
                # Get district name
                district = db.query(District).filter(District.id == place.district_id).first()
                district_name = district.name if district else f"Quận {place.district_id}"
                address = place.address_detail or f"Quận {district_name}, Hà Nội"
                
                recent_favorites.append({
                    "id": place.id,
                    "name": place.name,
                    "district_id": place.district_id,
                    "district_name": district_name,
                    "address": address,
                    "place_type_id": place.place_type_id,
                    "rating_average": float(place.rating_average) if place.rating_average else 0,
                    "rating_count": place.rating_count or 0,
                    "price_min": price_min,
                    "price_max": price_max,
                    "main_image_url": get_main_image_url(place.id, db)
                })
        
        # Get recent posts from MongoDB
        recent_posts = []
        try:
            user_posts = await mongo_client.find_many(
                "posts", 
                {"author_id": user_id, "status": "approved"},
                sort=[("created_at", -1)],
                limit=5
            )
            for post in user_posts:
                recent_posts.append({
                    "_id": str(post.get("_id")),
                    "title": post.get("title"),
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
                })
        except Exception as e:
            logger.warning(f"Error getting user posts: {e}")
        
        # Stats with MongoDB posts count
        posts_count = 0
        try:
            posts_count = await mongo_client.count("posts", {"author_id": user_id})
        except Exception as e:
            logger.warning(f"Error counting posts: {e}")
        
        stats = {
            "posts_count": posts_count,
            "favorites_count": db.query(UserPlaceFavorite).filter(
                UserPlaceFavorite.user_id == user_id
            ).count()
        }
        
        return success_response(
            message="Lấy thông tin profile thành công",
            data={
                "user": {
                    # Swagger UserDetailResponse.data.user fields
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "avatar_url": get_avatar_url(user.avatar_url),  # Normalized to full URL
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
                    "avatar_url": get_avatar_url(user.avatar_url),
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


# ==================== ALIAS ENDPOINTS (For Frontend Compatibility) ====================

@router.get("/profile", summary="Get Profile (Alias)")
async def get_profile_alias(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Alias cho GET /users/me - Tương thích với frontend
    Returns data directly as UserProfile (not nested in 'user')
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        
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
                price_min = float(place.price_min) if place.price_min else 0
                price_max = float(place.price_max) if place.price_max else 0
                if price_min > price_max:
                    price_min, price_max = price_max, price_min
                
                # Get district name
                district = db.query(District).filter(District.id == place.district_id).first()
                district_name = district.name if district else f"Quận {place.district_id}"
                
                recent_favorites.append({
                    "id": place.id,
                    "name": place.name,
                    "district_id": place.district_id,
                    "district_name": district_name,
                    "address": place.address_detail or f"Quận {district_name}, Hà Nội",
                    "place_type_id": place.place_type_id,
                    "rating_average": float(place.rating_average) if place.rating_average else 0,
                    "rating_count": place.rating_count or 0,
                    "price_min": price_min,
                    "price_max": price_max,
                    "main_image_url": get_main_image_url(place.id, db)
                })
        
        # Get recent posts from MongoDB
        recent_posts = []
        try:
            user_posts = await mongo_client.find_many(
                "posts", 
                {"author_id": user_id, "status": "approved"},
                sort=[("created_at", -1)],
                limit=5
            )
            for post in user_posts:
                recent_posts.append({
                    "_id": str(post.get("_id")),
                    "author": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "avatar_url": get_avatar_url(user.avatar_url),
                        "role_id": user.role_id
                    },
                    "title": post.get("title"),
                    "content": post.get("content", ""),
                    "images": post.get("images", []),
                    "likes_count": post.get("likes_count", 0),
                    "comments_count": post.get("comments_count", 0),
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
                })
        except Exception as e:
            logger.warning(f"Error getting user posts: {e}")
        
        # Return flat structure matching frontend UserDetailResponse type
        return success_response(
            message="Lấy thông tin profile thành công",
            data={
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "avatar_url": get_avatar_url(user.avatar_url),
                "bio": user.bio,
                "role_id": user.role_id,
                "reputation_score": user.reputation_score,
                "is_active": user.is_active,
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


@router.put("/profile", summary="Update Profile (Alias)")
async def update_profile_alias(
    request: Request,
    update_data: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Alias cho PUT /users/me - Tương thích với frontend
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
                    "avatar_url": get_avatar_url(user.avatar_url),
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


@router.get("/{user_id}", summary="Get User by ID")
async def get_user_by_id(
    request: Request,
    user_id: int = Path(..., description="ID của user"),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin public của user khác
    """
    try:
        await get_mongodb()
        
        user = db.query(User).filter(User.id == user_id, User.deleted_at == None).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Get user's recent favorites
        favorites = db.query(UserPlaceFavorite).filter(
            UserPlaceFavorite.user_id == user_id
        ).order_by(UserPlaceFavorite.created_at.desc()).limit(5).all()
        
        recent_favorites = []
        for fav in favorites:
            place = db.query(Place).filter(Place.id == fav.place_id).first()
            if place:
                price_min = float(place.price_min) if place.price_min else 0
                price_max = float(place.price_max) if place.price_max else 0
                if price_min > price_max:
                    price_min, price_max = price_max, price_min
                
                district = db.query(District).filter(District.id == place.district_id).first()
                district_name = district.name if district else f"Quận {place.district_id}"
                
                recent_favorites.append({
                    "id": place.id,
                    "name": place.name,
                    "district_id": place.district_id,
                    "district_name": district_name,
                    "address": place.address_detail or f"Quận {district_name}, Hà Nội",
                    "place_type_id": place.place_type_id,
                    "rating_average": float(place.rating_average) if place.rating_average else 0,
                    "rating_count": place.rating_count or 0,
                    "price_min": price_min,
                    "price_max": price_max,
                    "main_image_url": get_main_image_url(place.id, db)
                })
        
        # Get recent posts from MongoDB with image normalization
        recent_posts = []
        try:
            user_posts = await mongo_client.find_many(
                "posts", 
                {"author_id": user_id, "status": "approved"},
                sort=[("created_at", -1)],
                limit=5
            )
            
            for post in user_posts:
                recent_posts.append({
                    "_id": str(post.get("_id")),
                    "author": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "avatar_url": get_avatar_url(user.avatar_url),
                        "role_id": user.role_id
                    },
                    "title": post.get("title"),
                    "content": post.get("content", ""),
                    "images": normalize_image_list(post.get("images", [])),
                    "likes_count": post.get("likes_count", 0),
                    "comments_count": post.get("comments_count", 0),
                    "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
                })
        except Exception as e:
            logger.warning(f"Error getting user posts: {e}")
        
        return success_response(
            message="Lấy thông tin user thành công",
            data={
                "id": user.id,
                "full_name": user.full_name,
                "avatar_url": get_avatar_url(user.avatar_url),
                "bio": user.bio,
                "role_id": user.role_id,
                "reputation_score": user.reputation_score,
                "recent_favorites": recent_favorites,
                "recent_posts": recent_posts
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting user by id: {str(e)}")
        return error_response(
            message="Lỗi lấy thông tin user",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/avatar", summary="Upload Avatar")
async def upload_avatar(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload avatar mới cho user
    """
    from fastapi import File, UploadFile
    from app.utils.image_helpers import save_avatar_image
    
    try:
        user_id = current_user.get("user_id")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="USER_NOT_FOUND",
                status_code=404
            )
        
        # Get form data
        form = await request.form()
        avatar_file = form.get("avatar")
        
        if not avatar_file:
            return error_response(
                message="Không tìm thấy file avatar",
                error_code="NO_FILE",
                status_code=400
            )
        
        # Validate file type
        content_type = avatar_file.content_type
        if content_type not in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
            return error_response(
                message="Chỉ chấp nhận file ảnh (JPEG, PNG, GIF, WebP)",
                error_code="INVALID_FILE_TYPE",
                status_code=400
            )
        
        # Save using helper function
        result = await save_avatar_image(avatar_file, user_id)
        
        # Log for debugging
        logger.info(f"Avatar upload result for user {user_id}:")
        logger.info(f"  - relative_path (stored in DB): {result['relative_path']}")
        logger.info(f"  - url (returned to frontend): {result['url']}")
        logger.info(f"  - filename: {result['filename']}")
        
        # Save relative path to database (e.g., "/static/uploads/avatars/avatar_1_abc123.jpg")
        user.avatar_url = result["relative_path"]
        db.commit()
        
        # Return full URL to frontend immediately
        return success_response(
            message="Upload avatar thành công",
            data={
                "url": result["url"]  # Full URL for immediate display
            }
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading avatar: {str(e)}")
        return error_response(
            message="Lỗi upload avatar",
            error_code="INTERNAL_ERROR",
            status_code=500
        )



@router.delete("/avatar", summary="Delete Avatar")
async def delete_avatar(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa avatar của user
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
        
        # Clear avatar_url
        user.avatar_url = None
        db.commit()
        
        return success_response(message="Đã xóa avatar")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting avatar: {str(e)}")
        return error_response(
            message="Lỗi xóa avatar",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF USERS ROUTES ====================
