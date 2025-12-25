"""
Admin API Routes

Module này định nghĩa các API endpoints cho Admin Panel:
- POST /admin/login - Đăng nhập admin
- POST /admin/logout - Đăng xuất admin
- GET /admin/dashboard - Thống kê dashboard
- User Management: GET, DELETE, PATCH ban/unban
- Post Management: GET, POST, PUT, DELETE, PATCH status
- Comment Management: GET, DELETE
- Report Management: GET
- Place Management: GET, POST, PUT, DELETE

Swagger v1.0.5 Compatible
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Path, Query
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
import logging

from config.database import (
    get_db, User, Role, Place, PlaceType, District, 
    PlaceImage, Restaurant, Hotel, TouristAttraction
)
from middleware.auth import get_current_user, auth_middleware
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

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


# ==================== AUTH ENDPOINTS ====================

@router.post("/login", summary="Admin Login")
async def admin_login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Đăng nhập admin"""
    try:
        # Find user
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            return error_response(
                message="Email hoặc mật khẩu không đúng",
                error_code="INVALID_CREDENTIALS",
                status_code=401
            )
        
        # Check password
        if not auth_middleware.verify_password(login_data.password, user.password_hash):
            return error_response(
                message="Email hoặc mật khẩu không đúng",
                error_code="INVALID_CREDENTIALS",
                status_code=401
            )
        
        # Check role
        if user.role_id not in [1, 2]:  # 1=admin, 2=moderator
            return error_response(
                message="Bạn không có quyền truy cập admin",
                error_code="FORBIDDEN",
                status_code=403
            )
        
        # Check active
        if not user.is_active:
            return error_response(
                message="Tài khoản đã bị khóa",
                error_code="ACCOUNT_BANNED",
                status_code=403
            )
        
        # Generate tokens
        access_token = auth_middleware.create_access_token(user)
        
        return success_response(
            message="Đăng nhập thành công",
            data={
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "role_id": user.role_id
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return error_response(
            message="Lỗi đăng nhập",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/logout", summary="Admin Logout")
async def admin_logout(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Đăng xuất admin"""
    return success_response(message="Đăng xuất thành công")


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
        
        # Place stats
        total_places = db.query(Place).filter(Place.deleted_at == None).count()
        
        # Post stats from MongoDB
        try:
            total_posts = await mongo_client.count("posts", {})
            pending_posts = await mongo_client.count("posts", {"status": "pending"})
        except:
            total_posts = 0
            pending_posts = 0
        
        return success_response(
            message="Lấy thống kê thành công",
            data={
                "total_users": total_users,
                "active_users": active_users,
                "total_posts": total_posts,
                "pending_posts": pending_posts,
                "total_places": total_places
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
        query = db.query(User)
        
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
                "avatar_url": user.avatar_url,
                "role_id": user.role_id,
                "is_active": user.is_active,
                "ban_reason": user.ban_reason,
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
        user.deleted_at = datetime.utcnow()
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
        
        # Format posts
        formatted_posts = []
        for post in posts:
            user = db.query(User).filter(User.id == post.get("author_id")).first()
            formatted_posts.append({
                "_id": str(post.get("_id")),
                "title": post.get("title"),
                "author": {
                    "id": user.id if user else None,
                    "full_name": user.full_name if user else "Unknown"
                } if user else None,
                "status": post.get("status"),
                "likes_count": post.get("likes_count", 0),
                "comments_count": post.get("comments_count", 0),
                "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
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
    """Tạo post (auto-approved)"""
    try:
        await get_mongodb()
        
        post_doc = {
            "type": "post",
            "author_id": current_user.get("user_id"),
            "title": post_data.title,
            "content": post_data.content,
            "images": post_data.images or [],
            "tags": post_data.tags or [],
            "related_place_id": post_data.related_place_id,
            "rating": post_data.rating,
            "likes_count": 0,
            "comments_count": 0,
            "status": "approved"  # Auto-approve for admin
        }
        
        post_id = await mongo_client.create_post(post_doc)
        
        return success_response(
            message="Tạo bài viết thành công",
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


@router.delete("/posts/{post_id}", summary="Delete Post")
async def delete_post(
    request: Request,
    post_id: str = Path(...),
    current_user: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Xóa post"""
    try:
        await get_mongodb()
        from bson import ObjectId
        
        success = await mongo_client.delete_one("posts", {"_id": ObjectId(post_id)})
        
        if not success:
            return error_response(
                message="Post không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        return success_response(message="Đã xóa post")
        
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
    """Approve hoặc reject post"""
    try:
        await get_mongodb()
        from bson import ObjectId
        
        update_data = {"status": status_data.status}
        if status_data.reason:
            update_data["reject_reason"] = status_data.reason
        
        success = await mongo_client.update_one(
            "posts", {"_id": ObjectId(post_id)}, update_data
        )
        
        if not success:
            return error_response(
                message="Post không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        return success_response(message=f"Đã cập nhật status thành {status_data.status}")
        
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
            formatted_comments.append({
                "_id": str(comment.get("_id")),
                "post_id": comment.get("post_id"),
                "user": {
                    "id": user.id if user else None,
                    "full_name": user.full_name if user else "Unknown"
                },
                "content": comment.get("content"),
                "parent_id": comment.get("parent_id"),
                "created_at": comment.get("created_at").isoformat() if comment.get("created_at") else None
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
        
        success = await mongo_client.delete_one("post_comments", {"_id": ObjectId(comment_id)})
        
        if not success:
            return error_response(
                message="Comment không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
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
            formatted_reports.append({
                "_id": str(report.get("_id")),
                "target_type": report.get("target_type"),
                "target_id": report.get("target_id"),
                "reporter": {
                    "id": reporter.id if reporter else None,
                    "full_name": reporter.full_name if reporter else "Unknown"
                },
                "reason": report.get("reason"),
                "description": report.get("description"),
                "created_at": report.get("created_at").isoformat() if report.get("created_at") else None
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
        query = db.query(Place).filter(Place.deleted_at == None)
        
        total = query.count()
        
        places = query.order_by(desc(Place.created_at))\
                      .offset((page - 1) * limit)\
                      .limit(limit)\
                      .all()
        
        place_list = []
        for place in places:
            place_list.append({
                "id": place.id,
                "name": place.name,
                "district_id": place.district_id,
                "place_type_id": place.place_type_id,
                "rating_average": float(place.rating_average) if place.rating_average else 0,
                "price_min": float(place.price_min) if place.price_min else 0,
                "price_max": float(place.price_max) if place.price_max else 0,
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
        
        # Add images
        for i, url in enumerate(place_data.images or []):
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
        
        place.deleted_at = datetime.utcnow()
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


# ==================== END OF ADMIN ROUTES ====================
