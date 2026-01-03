"""
Admin API Routes

Module này định nghĩa các API endpoints cho Admin Panel:
- GET /admin/dashboard - Thống kê dashboard
- User Management: GET, DELETE, PATCH ban/unban
- Post Management: GET, POST, PUT, DELETE, PATCH status
- Comment Management: GET, DELETE
- Report Management: GET
- Place Management: GET, POST, PUT, DELETE

Note: Admin authentication sử dụng /auth/login chung với users.
      AdminRoute ở frontend sẽ kiểm tra role để bảo vệ admin routes.

Swagger v1.0.5 Compatible
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Path, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from app.utils.timezone_helper import utc_now, to_iso_string
import logging

from config.database import (
    get_db, User, Role, Place, PlaceType, District, 
    PlaceImage, Restaurant, Hotel, TouristAttraction
)
from middleware.auth import get_current_user, auth_middleware
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb
from app.utils.image_helpers import get_avatar_url
from app.services.rating_sync import (
    on_post_approved, 
    on_post_rejected_or_deleted,
    sync_all_place_ratings,
    update_place_rating
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== DEPENDENCIES ====================

async def require_admin(request: Request, db: Session = Depends(get_db)):
    """Dependency kiểm tra admin role"""
    user = await auth_middleware.get_current_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập"
        )
    
    role = user.get("role", "user")
    if role not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập"
        )
    
    return user


# ==================== REQUEST SCHEMAS ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class BanUserRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class CreatePostRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    images: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    related_place_id: Optional[int] = None
    rating: Optional[float] = None


class UpdatePostStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(published|rejected)$")
    reason: Optional[str] = None


class PlaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    district_id: int
    place_type_id: int
    description: Optional[str] = None
    address_detail: Optional[str] = None
    latitude: float
    longitude: float
    open_hour: Optional[str] = None
    close_hour: Optional[str] = None
    price_min: Optional[float] = 0
    price_max: Optional[float] = 0
    images: Optional[List[str]] = []
    # Subtype fields
    cuisine_type: Optional[str] = None  # Restaurant
    star_rating: Optional[int] = None  # Hotel
    ticket_price: Optional[float] = None  # Attraction


# ==================== DASHBOARD ====================

@router.get("/dashboard", summary="Dashboard Stats")
async def get_dashboard(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy thống kê dashboard"""
    try:
        await get_mongodb()
        
        # User stats
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # New users today
        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = db.query(User).filter(User.created_at >= today_start).count()
        
        # Place stats
        total_places = db.query(Place).filter(Place.deleted_at == None).count()
        
        # Post stats from MongoDB
        try:
            total_posts = await mongo_client.count("posts", {})
            pending_posts = await mongo_client.count("posts", {"status": "pending"})
            # New posts today
            new_posts_today = await mongo_client.count("posts", {
                "created_at": {"$gte": today_start}
            })
        except:
            total_posts = 0
            pending_posts = 0
            new_posts_today = 0
        
        # Report stats from MongoDB
        try:
            total_reports = await mongo_client.count("reports", {})
        except:
            total_reports = 0
        
        return success_response(
            message="Lấy thống kê thành công",
            data={
                "total_users": total_users,
                "active_users": active_users,
                "new_users_today": new_users_today,
                "total_posts": total_posts,
                "pending_posts": pending_posts,
                "new_posts_today": new_posts_today,
                "total_places": total_places,
                "total_reports": total_reports
            }
        )
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return error_response(
            message="Lỗi lấy thống kê",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== USER MANAGEMENT ====================

@router.get("/users", summary="Manage Users")
async def get_users(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách users"""
    try:
        # Filter out soft-deleted users
        query = db.query(User).filter(User.deleted_at == None)
        
        # Filter
        if status_filter == "active":
            query = query.filter(User.is_active == True)
        elif status_filter == "banned":
            query = query.filter(User.is_active == False)
        
        # Count
        total = query.count()
        
        # Paginate
        users = query.order_by(desc(User.created_at))\
                     .offset((page - 1) * limit)\
                     .limit(limit)\
                     .all()
        
        # Format
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "avatar_url": get_avatar_url(user.avatar_url, user.id, user.full_name),
                "role_id": user.role_id,
                "is_active": user.is_active,
                "ban_reason": user.ban_reason,
                "reputation_score": user.reputation_score or 0,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return success_response(
            message="Lấy danh sách users thành công",
            data=user_list,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return error_response(
            message="Lỗi lấy danh sách users",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/users/{user_id}", summary="Delete User")
async def delete_user(
    request: Request,
    user_id: int = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa user (soft delete)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Soft delete
        user.deleted_at = utc_now()
        user.is_active = False
        db.commit()
        
        return success_response(message="Đã xóa user")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Delete user error: {str(e)}")
        return error_response(
            message="Lỗi xóa user",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.patch("/users/{user_id}/ban", summary="Ban User")
async def ban_user(
    request: Request,
    user_id: int = Path(...),
    ban_data: BanUserRequest = ...,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Ban user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        user.is_active = False
        user.ban_reason = ban_data.reason
        db.commit()
        
        return success_response(message="Đã ban user")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Ban user error: {str(e)}")
        return error_response(
            message="Lỗi ban user",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.patch("/users/{user_id}/unban", summary="Unban User")
async def unban_user(
    request: Request,
    user_id: int = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Unban user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(
                message="User không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        user.is_active = True
        user.ban_reason = None
        db.commit()
        
        return success_response(message="Đã unban user")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Unban user error: {str(e)}")
        return error_response(
            message="Lỗi unban user",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== POST MANAGEMENT ====================

@router.get("/posts", summary="Manage Posts")
async def get_admin_posts(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách posts cho admin"""
    try:
        from app.utils.image_helpers import get_avatar_url, normalize_image_list
        
        await get_mongodb()
        
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        skip = (page - 1) * limit
        
        posts = await mongo_client.find_many(
            "posts", query,
            sort=[("created_at", -1)],
            limit=limit, skip=skip
        )
        
        total = await mongo_client.count("posts", query)
        
        # Format posts with full information
        formatted_posts = []
        for post in posts:
            user = db.query(User).filter(User.id == post.get("author_id")).first()
            
            # Get related place info if exists
            related_place = None
            if post.get("related_place_id"):
                place = db.query(Place).filter(Place.id == post.get("related_place_id")).first()
                if place:
                    related_place = {
                        "id": place.id,
                        "name": place.name
                    }
            
            # Get avatar URL using helper
            avatar_url = None
            if user:
                avatar_url = get_avatar_url(user.avatar_url, user.id, user.full_name)
            
            # Normalize images with fallback to place images (đảm bảo ít nhất 2 ảnh)
            from app.utils.image_helpers import get_main_image_url, get_all_place_images
            images = normalize_image_list(post.get("images", []))
            
            # Fallback: Bù thêm ảnh từ địa điểm cho đủ 2 ảnh
            if post.get("related_place_id") and len(images) < 2:
                place_images = get_all_place_images(post.get("related_place_id"), db)
                for place_img in place_images:
                    if place_img not in images:
                        images.append(place_img)
                    if len(images) >= 2:
                        break
            
            # Check user status for display
            from app.utils.image_helpers import get_banned_user_avatar, get_deleted_user_avatar
            user_status = "active"
            user_display_name = user.full_name if user else "Unknown"
            user_avatar = avatar_url
            if user:
                if user.deleted_at is not None:
                    user_status = "deleted"
                    user_display_name = "Tài khoản bị xóa"
                    user_avatar = get_deleted_user_avatar()  # X mark with gray background
                elif not user.is_active:
                    user_status = "banned"
                    user_display_name = "Tài khoản bị ban"
                    user_avatar = get_banned_user_avatar()  # ! mark with red background
            
            formatted_posts.append({
                "_id": str(post.get("_id")),
                "title": post.get("title"),
                "content": post.get("content", ""),
                "images": images,
                "rating": post.get("rating"),
                "author": {
                    "id": user.id if user else None,
                    "full_name": user_display_name,
                    "avatar_url": user_avatar,
                    "is_banned": user_status != "active",
                    "status": user_status
                } if user else None,
                "related_place": related_place,
                "status": post.get("status"),
                "likes_count": post.get("likes_count", 0),
                "comments_count": post.get("comments_count", 0),
                "created_at": to_iso_string(post.get("created_at"))
            })
        
        return success_response(
            message="Lấy danh sách posts thành công",
            data=formatted_posts,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Get admin posts error: {str(e)}")
        return error_response(
            message="Lỗi lấy danh sách posts",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts", summary="Create Post (Admin)", status_code=201)
async def create_admin_post(
    request: Request,
    post_data: CreatePostRequest,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tạo post (auto-approved) - Tự động cập nhật rating của place liên quan"""
    try:
        await get_mongodb()
        
        # Convert full URLs to relative paths for database storage
        from app.utils.image_helpers import normalize_urls_to_relative_paths
        clean_images = normalize_urls_to_relative_paths(post_data.images or [])
        
        post_doc = {
            "type": "post",
            "author_id": current_user.get("user_id"),
            "title": post_data.title,
            "content": post_data.content,
            "images": clean_images,
            "tags": post_data.tags or [],
            "related_place_id": post_data.related_place_id,
            "rating": post_data.rating,
            "likes_count": 0,
            "comments_count": 0,
            "status": "approved"  # Auto-approve for admin
        }
        
        post_id = await mongo_client.create_post(post_doc)
        
        # Sync rating nếu post có related_place_id và rating (bao gồm cả rating = 0)
        rating_synced = False
        if post_data.related_place_id and post_data.rating is not None:
            rating_synced = await on_post_approved(post_doc, db, mongo_client)
        
        message = "Tạo bài viết thành công"
        if rating_synced:
            message += " và đã cập nhật rating của địa điểm"
        
        return success_response(
            message=message,
            data={"post_id": post_id}
        )
        
    except Exception as e:
        logger.error(f"Create admin post error: {str(e)}")
        return error_response(
            message="Lỗi tạo bài viết",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.put("/posts/{post_id}", summary="Update Post")
async def update_post(
    request: Request,
    post_id: str = Path(...),
    post_data: CreatePostRequest = ...,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật post"""
    try:
        await get_mongodb()
        from bson import ObjectId
        
        update_data = {
            "title": post_data.title,
            "content": post_data.content,
            "images": post_data.images or [],
            "tags": post_data.tags or [],
            "related_place_id": post_data.related_place_id,
            "rating": post_data.rating
        }
        
        success = await mongo_client.update_one(
            "posts", {"_id": ObjectId(post_id)}, update_data
        )
        
        if not success:
            return error_response(
                message="Post không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        return success_response(message="Cập nhật post thành công")
        
    except Exception as e:
        logger.error(f"Update post error: {str(e)}")
        return error_response(
            message="Lỗi cập nhật post",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


class DeletePostRequest(BaseModel):
    """Schema xóa bài viết"""
    reason: Optional[str] = Field(None, max_length=500)


@router.delete("/posts/{post_id}", summary="Delete Post")
async def delete_post(
    request: Request,
    post_id: str = Path(...),
    delete_data: Optional[DeletePostRequest] = None,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa post - Tự động cập nhật lại rating của place liên quan"""
    try:
        await get_mongodb()
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Lấy post trước khi xóa để có thông tin related_place_id và rating
        # Handle both ObjectId and string _id
        post = None
        post_query = None
        try:
            post_query = {"_id": ObjectId(post_id)}
            post = await mongo_client.find_one("posts", post_query)
        except InvalidId:
            pass
        
        if not post:
            post_query = {"_id": post_id}
            post = await mongo_client.find_one("posts", post_query)
        
        if not post:
            # Post không tồn tại, có thể đã bị xóa trước đó
            # Vẫn xóa reports liên quan để cleanup
            logger.warning(f"Post {post_id} not found, cleaning up related reports")
            try:
                deleted_reports = await mongo_client.db["reports_mongo"].delete_many({
                    "target_type": "post",
                    "target_id": post_id
                })
                logger.info(f"Deleted {deleted_reports.deleted_count} orphan reports for post {post_id}")
            except Exception as e:
                logger.warning(f"Error cleaning up orphan reports: {e}")
            
            return success_response(
                message="Bài viết đã được xóa trước đó. Đã dọn dẹp báo cáo liên quan."
            )
        
        success = await mongo_client.delete_one("posts", post_query)
        
        if not success:
            return error_response(
                message="Lỗi xóa post",
                error_code="DELETE_FAILED",
                status_code=500
            )
        
        # Also delete related likes, comments, and reports
        try:
            await mongo_client.db["post_likes_mongo"].delete_many({"post_id": post_id})
            await mongo_client.db["post_comments_mongo"].delete_many({"post_id": post_id})
            # Delete reports targeting this post
            await mongo_client.db["reports_mongo"].delete_many({
                "target_type": "post",
                "target_id": post_id
            })
        except Exception as e:
            logger.warning(f"Error deleting related data: {e}")
        
        # Recalculate rating nếu post có related_place_id và rating (bao gồm cả rating = 0)
        rating_synced = False
        if post.get("related_place_id") and post.get("rating") is not None and post.get("status") == "approved":
            rating_synced = await on_post_rejected_or_deleted(post, db, mongo_client)
        
        # Log với reason nếu có
        reason = delete_data.reason if delete_data else None
        message = "Đã xóa post"
        if reason:
            message += f" (Lý do: {reason})"
        if rating_synced:
            message += " và đã cập nhật lại rating của địa điểm"
        
        return success_response(message=message)
        
    except Exception as e:
        logger.error(f"Delete post error: {str(e)}")
        return error_response(
            message="Lỗi xóa post",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.patch("/posts/{post_id}/status", summary="Approve/Reject Post")
async def update_post_status(
    request: Request,
    post_id: str = Path(...),
    status_data: UpdatePostStatusRequest = ...,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve hoặc reject post - Tự động cập nhật rating của place liên quan"""
    try:
        await get_mongodb()
        from bson import ObjectId
        
        # Lấy post trước khi update để có thông tin related_place_id
        post = await mongo_client.find_one("posts", {"_id": ObjectId(post_id)})
        if not post:
            return error_response(
                message="Post không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Map status: published -> approved để thống nhất
        new_status = "approved" if status_data.status == "published" else status_data.status
        
        update_data = {"status": new_status}
        if status_data.reason:
            update_data["reject_reason"] = status_data.reason
        
        success = await mongo_client.update_one(
            "posts", {"_id": ObjectId(post_id)}, update_data
        )
        
        if not success:
            return error_response(
                message="Lỗi cập nhật post",
                error_code="UPDATE_FAILED",
                status_code=500
            )
        
        # Sync rating nếu post có related_place_id và rating (bao gồm cả rating = 0)
        rating_synced = False
        if post.get("related_place_id") and post.get("rating") is not None:
            if new_status == "approved":
                # Post được approve -> cập nhật rating
                rating_synced = await on_post_approved(post, db, mongo_client)
            elif new_status == "rejected":
                # Post bị reject -> recalculate rating (loại bỏ rating của post này)
                rating_synced = await on_post_rejected_or_deleted(post, db, mongo_client)
        
        # Cập nhật reputation_score của author khi post được approve/reject
        author_id = post.get("author_id")
        if author_id:
            from app.services.post_stats_sync import update_user_reputation
            await update_user_reputation(author_id, mongo_client)
            logger.info(f"Updated reputation for author {author_id} after post {post_id} status change to {new_status}")
        
        message = f"Đã cập nhật status thành {new_status}"
        if rating_synced:
            message += " và đã cập nhật rating của địa điểm"
        
        return success_response(message=message)
        
    except Exception as e:
        logger.error(f"Update post status error: {str(e)}")
        return error_response(
            message="Lỗi cập nhật status",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== COMMENT MANAGEMENT ====================

@router.get("/comments", summary="Manage Comments")
async def get_admin_comments(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách comments"""
    try:
        await get_mongodb()
        
        skip = (page - 1) * limit
        
        comments = await mongo_client.find_many(
            "post_comments", {},
            sort=[("created_at", -1)],
            limit=limit, skip=skip
        )
        
        total = await mongo_client.count("post_comments", {})
        
        formatted_comments = []
        for comment in comments:
            user = db.query(User).filter(User.id == comment.get("user_id")).first()
            # Check user status for display
            from app.utils.image_helpers import get_avatar_url, get_banned_user_avatar, get_deleted_user_avatar
            user_status = "active"
            user_display_name = user.full_name if user else "Unknown"
            user_avatar = None
            if user:
                if user.deleted_at is not None:
                    user_status = "deleted"
                    user_display_name = "Tài khoản bị xóa"
                    user_avatar = get_deleted_user_avatar()
                elif not user.is_active:
                    user_status = "banned"
                    user_display_name = "Tài khoản bị ban"
                    user_avatar = get_banned_user_avatar()
                else:
                    user_avatar = get_avatar_url(user.avatar_url, user.id, user.full_name)
            
            formatted_comments.append({
                "_id": str(comment.get("_id")),
                "post_id": comment.get("post_id"),
                "user": {
                    "id": user.id if user else None,
                    "full_name": user_display_name,
                    "avatar_url": user_avatar,
                    "is_banned": user_status != "active",
                    "status": user_status
                },
                "content": comment.get("content"),
                "parent_id": comment.get("parent_id"),
                "created_at": to_iso_string(comment.get("created_at"))
            })
        
        return success_response(
            message="Lấy danh sách comments thành công",
            data=formatted_comments,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Get comments error: {str(e)}")
        return error_response(
            message="Lỗi lấy comments",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/comments/{comment_id}", summary="Delete Comment")
async def delete_comment(
    request: Request,
    comment_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa comment"""
    try:
        await get_mongodb()
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Handle both ObjectId and string _id
        comment_query = None
        try:
            comment_query = {"_id": ObjectId(comment_id)}
        except InvalidId:
            comment_query = {"_id": comment_id}
        
        success = await mongo_client.delete_one("post_comments", comment_query)
        
        if not success:
            # Comment không tồn tại, có thể đã bị xóa trước đó
            # Vẫn xóa reports liên quan để cleanup
            logger.warning(f"Comment {comment_id} not found, cleaning up related reports")
            try:
                await mongo_client.db["reports_mongo"].delete_many({
                    "target_type": "comment",
                    "target_id": comment_id
                })
            except Exception as e:
                logger.warning(f"Error cleaning up orphan reports: {e}")
            
            return success_response(
                message="Comment đã được xóa trước đó. Đã dọn dẹp báo cáo liên quan."
            )
        
        # Delete reports targeting this comment
        try:
            await mongo_client.db["reports_mongo"].delete_many({
                "target_type": "comment",
                "target_id": comment_id
            })
        except Exception as e:
            logger.warning(f"Error deleting related reports: {e}")
        
        return success_response(message="Đã xóa comment")
        
    except Exception as e:
        logger.error(f"Delete comment error: {str(e)}")
        return error_response(
            message="Lỗi xóa comment",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== REPORT MANAGEMENT ====================

@router.get("/reports", summary="View Reports")
async def get_reports(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách reports"""
    try:
        await get_mongodb()
        
        skip = (page - 1) * limit
        
        reports = await mongo_client.find_many(
            "reports", {},
            sort=[("created_at", -1)],
            limit=limit, skip=skip
        )
        
        total = await mongo_client.count("reports", {})
        
        formatted_reports = []
        for report in reports:
            reporter = db.query(User).filter(User.id == report.get("reporter_id")).first()
            # Check reporter status for display
            reporter_status = "active"
            reporter_display_name = reporter.full_name if reporter else "Unknown"
            if reporter:
                if reporter.deleted_at is not None:
                    reporter_status = "deleted"
                    reporter_display_name = "Tài khoản bị xóa"
                elif not reporter.is_active:
                    reporter_status = "banned"
                    reporter_display_name = "Tài khoản bị ban"
            
            formatted_reports.append({
                "_id": str(report.get("_id")),
                "target_type": report.get("target_type"),
                "target_id": report.get("target_id"),
                "reporter": {
                    "id": reporter.id if reporter else None,
                    "full_name": reporter_display_name,
                    "is_banned": reporter_status != "active",
                    "status": reporter_status
                },
                "reason": report.get("reason"),
                "description": report.get("description"),
                "created_at": to_iso_string(report.get("created_at"))
            })
        
        return success_response(
            message="Lấy danh sách reports thành công",
            data=formatted_reports,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Get reports error: {str(e)}")
        return error_response(
            message="Lỗi lấy reports",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/reports/{report_id}", summary="Dismiss Report")
async def dismiss_report(
    request: Request,
    report_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Bỏ qua (xóa) một báo cáo"""
    try:
        await get_mongodb()
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Handle both ObjectId and string _id
        report_query = None
        try:
            report_query = {"_id": ObjectId(report_id)}
        except InvalidId:
            report_query = {"_id": report_id}
        
        # Check if report exists
        report = await mongo_client.find_one("reports", report_query)
        if not report:
            return error_response(
                message="Báo cáo không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Delete the report
        success = await mongo_client.delete_one("reports", report_query)
        
        if not success:
            return error_response(
                message="Lỗi xóa báo cáo",
                error_code="DELETE_FAILED",
                status_code=500
            )
        
        logger.info(f"Admin {current_user.get('user_id')} dismissed report {report_id}")
        
        return success_response(message="Đã bỏ qua báo cáo")
        
    except Exception as e:
        logger.error(f"Dismiss report error: {str(e)}")
        return error_response(
            message="Lỗi xóa báo cáo",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== PLACE MANAGEMENT ====================

@router.get("/places", summary="Manage Places")
async def get_admin_places(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Lấy danh sách places cho admin"""
    try:
        from app.utils.image_helpers import get_main_image_url
        
        query = db.query(Place).filter(Place.deleted_at == None)
        
        total = query.count()
        
        places = query.order_by(desc(Place.created_at))\
                      .offset((page - 1) * limit)\
                      .limit(limit)\
                      .all()
        
        # Batch sync ratings from MongoDB for all places on screen
        place_ids = [place.id for place in places]
        if place_ids:
            try:
                from app.services.rating_sync import sync_places_ratings_batch
                synced_ratings = await sync_places_ratings_batch(place_ids, db, mongo_client)
                logger.info(f"[ADMIN] Synced ratings for {len(synced_ratings)} places")
                # Refresh places after sync
                db.expire_all()
                places = query.order_by(desc(Place.created_at))\
                              .offset((page - 1) * limit)\
                              .limit(limit)\
                              .all()
            except Exception as sync_error:
                logger.warning(f"[ADMIN] Rating sync failed: {sync_error}")
        
        place_list = []
        for place in places:
            # Auto-swap nếu giá trị bị đảo ngược trong database
            price_min = float(place.price_min) if place.price_min else 0
            price_max = float(place.price_max) if place.price_max else 0
            # Swap khi price_min > price_max (dữ liệu bị lưu ngược)
            if price_min > price_max:
                price_min, price_max = price_max, price_min
            
            # Get district name
            district = db.query(District).filter(District.id == place.district_id).first()
            district_name = district.name if district else f"Quận {place.district_id}"
            
            # Get main image
            main_image_url = get_main_image_url(place.id, db)
            
            # Build address - avoid duplicate "Quận" prefix
            if place.address_detail:
                address = place.address_detail
            elif district_name.startswith("Quận "):
                address = f"{district_name}, Hà Nội"
            else:
                address = f"Quận {district_name}, Hà Nội"
            
            place_list.append({
                "id": place.id,
                "name": place.name,
                "district_id": place.district_id,
                "district_name": district_name,
                "address": address,
                "description": place.description or "",
                "place_type_id": place.place_type_id,
                "rating_average": float(place.rating_average) if place.rating_average else 0,
                "rating_count": place.rating_count or 0,
                "price_min": price_min,
                "price_max": price_max,
                "main_image_url": main_image_url,
                "latitude": float(place.latitude) if place.latitude else None,
                "longitude": float(place.longitude) if place.longitude else None,
                "created_at": place.created_at.isoformat() if place.created_at else None
            })
        
        return success_response(
            message="Lấy danh sách places thành công",
            data=place_list,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        logger.error(f"Get admin places error: {str(e)}")
        return error_response(
            message="Lỗi lấy danh sách places",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/places", summary="Create Place", status_code=201)
async def create_place(
    request: Request,
    place_data: PlaceCreateRequest,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Tạo place mới"""
    try:
        from datetime import time
        
        # Parse time strings
        open_hour = None
        close_hour = None
        if place_data.open_hour:
            h, m = map(int, place_data.open_hour.split(':'))
            open_hour = time(h, m)
        if place_data.close_hour:
            h, m = map(int, place_data.close_hour.split(':'))
            close_hour = time(h, m)
        
        # Create place
        place = Place(
            name=place_data.name,
            district_id=place_data.district_id,
            place_type_id=place_data.place_type_id,
            description=place_data.description,
            address_detail=place_data.address_detail,
            latitude=place_data.latitude,
            longitude=place_data.longitude,
            open_hour=open_hour,
            close_hour=close_hour,
            price_min=place_data.price_min or 0,
            price_max=place_data.price_max or 0
        )
        
        db.add(place)
        db.flush()  # Get ID
        
        # Add images - rename temp files to proper format
        from pathlib import Path as FilePath
        import shutil
        import re
        from config.image_config import get_uploads_base_url
        
        src_dir = FilePath(__file__).resolve().parent.parent.parent.parent  # app/api/v1 -> app -> src/backend -> src
        uploads_dir = src_dir / "static" / "uploads" / "places"
        base_url = get_uploads_base_url()
        
        misc_dir = src_dir / "static" / "uploads" / "misc"
        
        renamed_urls = []
        for i, url in enumerate(place_data.images or []):
            # Extract filename from URL
            # URL format: http://.../.../place_{uuid}.jpg or /static/uploads/places/place_{uuid}.jpg
            filename = url.split('/')[-1] if '/' in url else url
            
            # Check if this is a temp file (place_{uuid}.ext) or generic UUID file
            # UUID format: place_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.ext
            # or just: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.ext (from misc folder)
            is_temp_place = re.match(r'^place_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\..+$', filename)
            is_misc_uuid = re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\..+$', filename)
            
            if is_temp_place or is_misc_uuid:
                # This is a temp file, rename it
                ext = filename.rsplit('.', 1)[1] if '.' in filename else 'jpg'
                new_filename = f"place_{place.id}_{i}.{ext}"
                
                # Check places folder first, then misc folder
                old_path = uploads_dir / filename
                if not old_path.exists():
                    old_path = misc_dir / filename
                
                new_path = uploads_dir / new_filename
                
                if old_path.exists():
                    try:
                        shutil.move(str(old_path), str(new_path))
                        logger.info(f"Renamed {filename} -> {new_filename}")
                        # Update URL to new filename - new format: folder/filename
                        new_url = f"places/{new_filename}"
                        renamed_urls.append(new_url)
                    except Exception as rename_error:
                        logger.warning(f"Could not rename {filename}: {rename_error}")
                        renamed_urls.append(url)  # Keep original URL
                else:
                    # File doesn't exist locally, might be cloud URL - keep as is
                    logger.warning(f"File not found: {filename} in places or misc folder")
                    renamed_urls.append(url)
            else:
                # Not a temp file, keep original URL
                renamed_urls.append(url)
        
        # Add images with renamed URLs
        for i, url in enumerate(renamed_urls):
            img = PlaceImage(
                place_id=place.id,
                image_url=url,
                is_main=(i == 0)
            )
            db.add(img)
        
        # Add subtype
        if place_data.place_type_id == 1 and place_data.cuisine_type:  # Restaurant
            restaurant = Restaurant(
                place_id=place.id,
                cuisine_type=place_data.cuisine_type
            )
            db.add(restaurant)
        elif place_data.place_type_id == 2 and place_data.star_rating:  # Hotel
            hotel = Hotel(
                place_id=place.id,
                star_rating=place_data.star_rating
            )
            db.add(hotel)
        elif place_data.place_type_id == 3 and place_data.ticket_price is not None:  # Attraction
            attraction = TouristAttraction(
                place_id=place.id,
                ticket_price=place_data.ticket_price
            )
            db.add(attraction)
        
        db.commit()
        
        return success_response(
            message="Tạo địa điểm thành công",
            data={"place_id": place.id}
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Create place error: {str(e)}")
        return error_response(
            message="Lỗi tạo địa điểm",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.put("/places/{place_id}", summary="Update Place")
async def update_place(
    request: Request,
    place_id: int = Path(...),
    place_data: PlaceCreateRequest = ...,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cập nhật place"""
    try:
        from datetime import time
        
        place = db.query(Place).filter(Place.id == place_id).first()
        if not place:
            return error_response(
                message="Địa điểm không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Update fields
        place.name = place_data.name
        place.district_id = place_data.district_id
        place.place_type_id = place_data.place_type_id
        place.description = place_data.description
        place.address_detail = place_data.address_detail
        place.latitude = place_data.latitude
        place.longitude = place_data.longitude
        place.price_min = place_data.price_min or 0
        place.price_max = place_data.price_max or 0
        
        if place_data.open_hour:
            h, m = map(int, place_data.open_hour.split(':'))
            place.open_hour = time(h, m)
        if place_data.close_hour:
            h, m = map(int, place_data.close_hour.split(':'))
            place.close_hour = time(h, m)
        
        # Update images if provided
        if place_data.images is not None:
            # Remove old images
            db.query(PlaceImage).filter(PlaceImage.place_id == place_id).delete()
            
            # Add new images
            for i, url in enumerate(place_data.images):
                img = PlaceImage(
                    place_id=place.id,
                    image_url=url,
                    is_main=(i == 0)
                )
                db.add(img)
        
        db.commit()
        
        return success_response(message="Cập nhật địa điểm thành công")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Update place error: {str(e)}")
        return error_response(
            message="Lỗi cập nhật địa điểm",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/places/{place_id}", summary="Delete Place")
async def delete_place(
    request: Request,
    place_id: int = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa place (soft delete)"""
    try:
        place = db.query(Place).filter(Place.id == place_id).first()
        if not place:
            return error_response(
                message="Địa điểm không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        place.deleted_at = utc_now()
        db.commit()
        
        return success_response(message="Đã xóa địa điểm")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Delete place error: {str(e)}")
        return error_response(
            message="Lỗi xóa địa điểm",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== RATING SYNC ====================

@router.post("/sync-ratings", summary="Sync All Place Ratings")
async def sync_ratings(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Đồng bộ rating của TẤT CẢ places từ MongoDB posts.
    Chạy batch job để tính toán lại rating_average và rating_count.
    Chỉ admin mới có thể chạy.
    """
    try:
        await get_mongodb()
        
        logger.info(f"[ADMIN] Starting rating sync by user {current_user.get('user_id')}")
        
        result = await sync_all_place_ratings(db, mongo_client)
        
        if "error" in result:
            return error_response(
                message=f"Lỗi đồng bộ rating: {result['error']}",
                error_code="SYNC_FAILED",
                status_code=500
            )
        
        return success_response(
            message="Đồng bộ rating thành công",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Sync ratings error: {str(e)}")
        return error_response(
            message="Lỗi đồng bộ rating",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/places/{place_id}/sync-rating", summary="Sync Single Place Rating")
async def sync_single_place_rating(
    request: Request,
    place_id: int = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Đồng bộ rating cho một place cụ thể từ MongoDB posts.
    """
    try:
        await get_mongodb()
        
        # Check place exists
        place = db.query(Place).filter(Place.id == place_id).first()
        if not place:
            return error_response(
                message="Địa điểm không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        success = await update_place_rating(place_id, db, mongo_client)
        
        if not success:
            return error_response(
                message="Lỗi cập nhật rating",
                error_code="UPDATE_FAILED",
                status_code=500
            )
        
        # Lấy rating mới sau khi cập nhật
        db.refresh(place)
        
        return success_response(
            message="Đã cập nhật rating cho địa điểm",
            data={
                "place_id": place_id,
                "rating_average": float(place.rating_average) if place.rating_average else 0,
                "rating_count": place.rating_count or 0
            }
        )
        
    except Exception as e:
        logger.error(f"Sync place rating error: {str(e)}")
        return error_response(
            message="Lỗi cập nhật rating",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF ADMIN ROUTES ====================
