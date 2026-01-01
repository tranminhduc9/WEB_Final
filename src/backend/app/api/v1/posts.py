"""
Posts API Routes

Module này định nghĩa các API endpoints cho Posts bao gồm:
- GET /posts - Lấy danh sách bài viết (feed)
- POST /posts - Tạo bài viết mới
- GET /posts/{id} - Chi tiết bài viết
- POST /posts/{id}/like - Toggle like
- POST /posts/{id}/comments - Thêm comment
- POST /comments/{id}/reply - Reply comment
- POST /posts/{id}/favorite - Toggle favorite
- POST /posts/{id}/report - Báo cáo bài viết
- POST /comments/{id}/report - Báo cáo comment

Swagger v1.0.5 Compatible - MongoDB Integration
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Path, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils.timezone_helper import utc_now
import logging
import os

from config.database import get_db, User, UserPostFavorite, Place
from app.utils.image_helpers import get_main_image_url, get_post_images
from app.utils.place_helpers import get_place_compact, get_user_compact
from app.utils.content_sanitizer import (
    sanitize_post_title, sanitize_post_content, sanitize_comment,
    sanitize_tags, sanitize_image_urls, sanitize_report_reason,
    sanitize_report_description, detect_xss_attempt, log_security_event
)
from middleware.auth import get_current_user, get_optional_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb
from app.services.logging_service import log_activity, log_visit

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Posts"])


# ==================== REQUEST SCHEMAS ====================

class CreatePostRequest(BaseModel):
    """Schema tạo bài viết"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    images: Optional[List[str]] = Field(default=[])
    tags: Optional[List[str]] = Field(default=[])
    related_place_id: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=5)


class CreateCommentRequest(BaseModel):
    """Schema tạo comment"""
    content: str = Field(..., min_length=1, max_length=2000)
    images: Optional[List[str]] = Field(default=[])


class CreateReplyRequest(BaseModel):
    """Schema tạo reply"""
    content: str = Field(..., min_length=1, max_length=2000)
    images: Optional[List[str]] = Field(default=[])


class ReportRequest(BaseModel):
    """Schema báo cáo"""
    reason: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)




async def format_post_response(post: Dict, db: Session, current_user_id: int = None) -> Dict:
    """Format post cho response"""
    author = get_user_compact(post.get("author_id"), db)
    related_place = None
    if post.get("related_place_id"):
        related_place = get_place_compact(post.get("related_place_id"), db)
    
    # Check if current user liked
    is_liked = False
    if current_user_id:
        like = await mongo_client.find_one("post_likes", {
            "post_id": str(post.get("_id")),
            "user_id": current_user_id
        })
        is_liked = like is not None
    
    # Get post images - chỉ cần gọi helper function
    post_images = get_post_images(post)
    
    # Fallback: Nếu không có ảnh nhưng có related_place_id, dùng ảnh của địa điểm
    if not post_images and post.get("related_place_id"):
        place_image = get_main_image_url(post.get("related_place_id"), db)
        if place_image:
            post_images = [place_image]
    
    return {
        "_id": str(post.get("_id")),
        "author": author,
        "title": post.get("title"),
        "content": post.get("content"),
        "rating": post.get("rating"),
        "related_place": related_place,
        "images": post_images,
        "tags": post.get("tags", []),
        "likes_count": post.get("likes_count", 0),
        "comments_count": post.get("comments_count", 0),
        "is_liked": is_liked,
        "status": post.get("status"),
        "created_at": post.get("created_at").isoformat() if post.get("created_at") else None
    }


# ==================== POSTS ENDPOINTS ====================

@router.get("/posts", summary="View Post Feed")
async def get_posts(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bài viết (feed)
    Chỉ lấy bài viết đã approved
    """
    try:
        await get_mongodb()
        
        skip = (page - 1) * limit
        
        # Query posts from MongoDB - sắp xếp theo popular (nhiều like nhất)
        posts = await mongo_client.get_posts(limit=limit, skip=skip, sort="popular")
        
        # Sync stats batch cho tất cả posts
        from app.services.post_stats_sync import sync_posts_stats_batch
        post_ids = [str(post.get("_id")) for post in posts]
        synced_stats = await sync_posts_stats_batch(post_ids, mongo_client)
        
        # Count total
        total = await mongo_client.count("posts", {"status": "approved"})
        
        # Format response with synced stats
        current_user_id = current_user.get("user_id") if current_user else None
        formatted_posts = []
        for post in posts:
            post_id = str(post.get("_id"))
            # Apply synced stats to post
            if post_id in synced_stats:
                post["likes_count"] = synced_stats[post_id]["likes_count"]
                post["comments_count"] = synced_stats[post_id]["comments_count"]
            formatted = await format_post_response(post, db, current_user_id)
            formatted_posts.append(formatted)
        
        return success_response(
            message="Lấy danh sách bài viết thành công",
            data={
                "posts": formatted_posts,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_items": total,
                    "total_pages": (total + limit - 1) // limit
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting posts: {str(e)}")
        return error_response(
            message="Lỗi lấy danh sách bài viết",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts", summary="Create Post", status_code=201)
async def create_post(
    request: Request,
    post_data: CreatePostRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo bài viết mới
    Status mặc định là 'pending', cần admin approve
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        
        # Sanitize user inputs
        clean_title = sanitize_post_title(post_data.title)
        clean_content = sanitize_post_content(post_data.content)
        clean_tags = sanitize_tags(post_data.tags or [])
        clean_images = sanitize_image_urls(post_data.images or [])
        
        # Log security event if XSS attempt detected
        if detect_xss_attempt(post_data.content) or detect_xss_attempt(post_data.title):
            client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
            log_security_event("xss_attempt", post_data.content, user_id, client_ip)
        
        # Prepare post document with sanitized data
        post_doc = {
            "type": "post",
            "author_id": user_id,
            "title": clean_title,
            "content": clean_content,
            "images": clean_images,
            "tags": clean_tags,
            "related_place_id": post_data.related_place_id,
            "rating": post_data.rating,
            "likes_count": 0,
            "comments_count": 0,
            "status": "pending"
        }
        
        # Insert to MongoDB
        post_id = await mongo_client.create_post(post_doc)
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="create_post",
            details=f"Tạo bài viết mới: {post_data.title[:50]}...",
            request=request
        )
        
        return success_response(
            message="Tạo bài viết thành công, đang chờ duyệt",
            data={"post_id": post_id}
        )
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return error_response(
            message="Lỗi tạo bài viết",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.get("/posts/{post_id}", summary="Post Details")
async def get_post_detail(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Lấy chi tiết bài viết kèm comments
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Get post - handle both ObjectId and UUID string as _id
        post = None
        try:
            post = await mongo_client.find_one("posts", {"_id": ObjectId(post_id)})
        except InvalidId:
            pass
        
        if not post:
            post = await mongo_client.find_one("posts", {"_id": post_id})
        
        if not post:
            return error_response(
                message="Bài viết không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Format post
        current_user_id = current_user.get("user_id") if current_user else None
        formatted_post = await format_post_response(post, db, current_user_id)
        
        # Get ALL comments (root + replies) for this post
        comments = await mongo_client.get_comments(post_id, limit=50)
        formatted_comments = []
        for comment in comments:
            user = get_user_compact(comment.get("user_id"), db)
            formatted_comments.append({
                "_id": str(comment.get("_id")),
                "user": user,
                "content": comment.get("content"),
                "parent_id": comment.get("parent_id"),
                "images": comment.get("images", []),
                "created_at": comment.get("created_at").isoformat() if comment.get("created_at") else None
            })
        
        formatted_post["comments"] = formatted_comments
        
        # Log visit
        try:
            user_id = current_user.get("user_id") if current_user else None
            await log_visit(
                db=db,
                request=request,
                user_id=user_id,
                post_id=post_id
            )
        except Exception as e:
            logger.error(f"Error logging visit: {e}")
        
        return success_response(
            message="Lấy chi tiết bài viết thành công",
            data=formatted_post
        )
        
    except Exception as e:
        logger.error(f"Error getting post detail: {str(e)}")
        return error_response(
            message="Lỗi lấy chi tiết bài viết",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts/{post_id}/like", summary="Toggle Like")
async def toggle_like(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like bài viết
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        user_id = current_user.get("user_id")
        
        # Find post - handle both ObjectId and string _id
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
            return error_response(
                message="Bài viết không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Toggle like
        result = await mongo_client.toggle_like(post_id, user_id)
        
        # Update likes_count using real-time handler
        from app.services.post_stats_sync import on_like_toggled
        await on_like_toggled(post_id, result["liked"], result["total_likes"], mongo_client)
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="like_post" if result["liked"] else "unlike_post",
            details=f"{'Like' if result['liked'] else 'Unlike'} bài viết ID: {post_id}",
            request=request
        )
        
        return {
            "success": True,
            "message": "Đã cập nhật like",
            "is_liked": result["liked"],
            "likes_count": result["total_likes"]
        }
        
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        return error_response(
            message="Lỗi cập nhật like",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts/{post_id}/comments", summary="Add Root Comment", status_code=201)
async def add_comment(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    comment_data: CreateCommentRequest = ...,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thêm comment vào bài viết (root comment)
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        user_id = current_user.get("user_id")
        
        # Find post - handle both ObjectId and string _id
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
            return error_response(
                message="Bài viết không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Sanitize comment content
        clean_content = sanitize_comment(comment_data.content)
        clean_images = sanitize_image_urls(comment_data.images or [])
        
        # Log security event if XSS attempt detected
        if detect_xss_attempt(comment_data.content):
            client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
            log_security_event("xss_attempt_comment", comment_data.content, user_id, client_ip)
        
        comment_doc = {
            "post_id": post_id,
            "user_id": user_id,
            "content": clean_content,
            "images": clean_images,
            "parent_id": None  # Root comment
        }
        
        comment_id = await mongo_client.create_comment(comment_doc)
        
        # Update comments_count using real-time handler
        from app.services.post_stats_sync import on_comment_added
        await on_comment_added(post_id, mongo_client)
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="create_comment",
            details=f"Comment bài viết ID: {post_id}",
            request=request
        )
        
        return success_response(
            message="Thêm comment thành công",
            data={
                "comment_id": comment_id,
                "created_at": utc_now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        return error_response(
            message="Lỗi thêm comment",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/comments/{comment_id}/reply", summary="Reply to Comment", status_code=201)
async def reply_to_comment(
    request: Request,
    comment_id: str = Path(..., description="Parent comment ID"),
    reply_data: CreateReplyRequest = ...,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reply một comment
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        user_id = current_user.get("user_id")
        
        # Verify parent comment exists - handle both ObjectId and string _id
        parent = None
        try:
            parent = await mongo_client.find_one("post_comments", {"_id": ObjectId(comment_id)})
        except InvalidId:
            pass
        
        if not parent:
            parent = await mongo_client.find_one("post_comments", {"_id": comment_id})
        
        if not parent:
            return error_response(
                message="Comment gốc không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Sanitize reply content
        clean_content = sanitize_comment(reply_data.content)
        
        # Log security event if XSS attempt detected
        if detect_xss_attempt(reply_data.content):
            client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
            log_security_event("xss_attempt_reply", reply_data.content, user_id, client_ip)
        
        reply_id = await mongo_client.create_reply(
            parent_id=comment_id,
            user_id=user_id,
            content=clean_content
        )
        
        # Update comments_count of post using real-time handler
        post_id = parent.get("post_id")
        from app.services.post_stats_sync import on_comment_added
        await on_comment_added(post_id, mongo_client)
        
        return success_response(
            message="Reply thành công",
            data={
                "comment_id": reply_id,
                "created_at": utc_now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error replying to comment: {str(e)}")
        return error_response(
            message="Lỗi reply comment",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts/{post_id}/favorite", summary="Toggle Favorite Post")
async def toggle_favorite_post(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle favorite bài viết (lưu vào PostgreSQL)
    """
    try:
        user_id = current_user.get("user_id")
        
        # Check if already favorited
        existing = db.query(UserPostFavorite).filter(
            UserPostFavorite.user_id == user_id,
            UserPostFavorite.post_id == post_id
        ).first()
        
        if existing:
            db.delete(existing)
            db.commit()
            is_favorited = False
            
            # Log activity
            await log_activity(
                db=db,
                user_id=user_id,
                action="unfavorite_post",
                details=f"Bỏ lưu bài viết ID: {post_id}",
                request=request
            )
        else:
            favorite = UserPostFavorite(user_id=user_id, post_id=post_id)
            db.add(favorite)
            db.commit()
            is_favorited = True
            
            # Log activity
            await log_activity(
                db=db,
                user_id=user_id,
                action="favorite_post",
                details=f"Lưu bài viết ID: {post_id}",
                request=request
            )
        
        return {
            "success": True,
            "message": "Đã cập nhật favorite",
            "is_favorited": is_favorited
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling favorite: {str(e)}")
        return error_response(
            message="Lỗi cập nhật favorite",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/posts/{post_id}/report", summary="Report Post")
async def report_post(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    report_data: ReportRequest = ...,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Báo cáo bài viết vi phạm
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        
        # Sanitize report data
        clean_reason = sanitize_report_reason(report_data.reason)
        clean_description = sanitize_report_description(report_data.description)
        
        report_doc = {
            "target_type": "post",
            "target_id": post_id,
            "reporter_id": user_id,
            "reason": clean_reason,
            "description": clean_description
        }
        
        await mongo_client.create_report(report_doc)
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="report_content",
            details=f"Báo cáo bài viết ID: {post_id} - Lý do: {report_data.reason}",
            request=request
        )
        
        return success_response(message="Đã gửi báo cáo")
        
    except Exception as e:
        logger.error(f"Error reporting post: {str(e)}")
        return error_response(
            message="Lỗi gửi báo cáo",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.post("/comments/{comment_id}/report", summary="Report Comment")
async def report_comment(
    request: Request,
    comment_id: str = Path(..., description="Comment ID"),
    report_data: ReportRequest = ...,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Báo cáo comment vi phạm
    """
    try:
        await get_mongodb()
        
        user_id = current_user.get("user_id")
        
        # Sanitize report data
        clean_reason = sanitize_report_reason(report_data.reason)
        clean_description = sanitize_report_description(report_data.description)
        
        report_doc = {
            "target_type": "comment",
            "target_id": comment_id,
            "reporter_id": user_id,
            "reason": clean_reason,
            "description": clean_description
        }
        
        await mongo_client.create_report(report_doc)
        
        return success_response(message="Đã gửi báo cáo")
        
    except Exception as e:
        logger.error(f"Error reporting comment: {str(e)}")
        return error_response(
            message="Lỗi gửi báo cáo",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/comments/{comment_id}", summary="Delete Comment")
async def delete_comment(
    request: Request,
    comment_id: str = Path(..., description="Comment ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa comment (chỉ owner hoặc admin mới có quyền)
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        user_id = current_user.get("user_id")
        user_role = current_user.get("role", "user")
        
        # Find comment - handle both ObjectId and string _id
        comment = None
        comment_query = None
        try:
            comment_query = {"_id": ObjectId(comment_id)}
            comment = await mongo_client.find_one("post_comments", comment_query)
        except InvalidId:
            pass
        
        if not comment:
            comment_query = {"_id": comment_id}
            comment = await mongo_client.find_one("post_comments", comment_query)
        
        if not comment:
            return error_response(
                message="Comment không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Check permission: owner or admin
        comment_owner_id = comment.get("user_id")
        is_owner = (comment_owner_id == user_id)
        is_admin = (user_role in ["admin", "moderator"])
        
        if not is_owner and not is_admin:
            return error_response(
                message="Bạn không có quyền xóa comment này",
                error_code="FORBIDDEN",
                status_code=403
            )
        
        # Delete the comment
        await mongo_client.delete_one("post_comments", comment_query)
        
        # Update post's comments_count using real-time handler
        post_id = comment.get("post_id")
        if post_id:
            from app.services.post_stats_sync import on_comment_deleted
            await on_comment_deleted(post_id, mongo_client)
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="delete_comment",
            details=f"Xóa comment ID: {comment_id}",
            request=request
        )
        
        return success_response(message="Đã xóa comment thành công")
        
    except Exception as e:
        logger.error(f"Error deleting comment: {str(e)}")
        return error_response(
            message="Lỗi xóa comment",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


@router.delete("/posts/{post_id}", summary="Delete Own Post")
async def delete_own_post(
    request: Request,
    post_id: str = Path(..., description="Post ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa bài viết của mình
    - Kiểm tra ownership: chỉ author mới xóa được
    - Cập nhật lại rating của place nếu bài viết có liên kết
    """
    try:
        await get_mongodb()
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        user_id = current_user.get("user_id")
        
        # Find post - handle both ObjectId and string _id
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
            return error_response(
                message="Bài viết không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Check ownership: only author can delete
        author_id = post.get("author_id")
        if author_id != user_id:
            return error_response(
                message="Bạn không có quyền xóa bài viết này",
                error_code="FORBIDDEN",
                status_code=403
            )
        
        # Delete the post
        success = await mongo_client.delete_one("posts", post_query)
        
        if not success:
            return error_response(
                message="Lỗi xóa bài viết",
                error_code="DELETE_FAILED",
                status_code=500
            )
        
        # Recalculate rating if post has related_place_id and rating
        rating_synced = False
        if post.get("related_place_id") and post.get("rating") is not None and post.get("status") == "approved":
            try:
                from app.services.rating_sync import on_post_rejected_or_deleted
                rating_synced = await on_post_rejected_or_deleted(post, db, mongo_client)
            except Exception as sync_error:
                logger.warning(f"Rating sync failed after post deletion: {sync_error}")
        
        # Also delete related favorites from PostgreSQL
        try:
            db.query(UserPostFavorite).filter(UserPostFavorite.post_id == post_id).delete()
            db.commit()
        except Exception as fav_error:
            logger.warning(f"Error deleting post favorites: {fav_error}")
            db.rollback()
        
        # Log activity
        await log_activity(
            db=db,
            user_id=user_id,
            action="delete_own_post",
            details=f"Xóa bài viết của mình ID: {post_id}",
            request=request
        )
        
        message = "Đã xóa bài viết thành công"
        if rating_synced:
            message += " và đã cập nhật lại rating của địa điểm"
        
        return success_response(message=message)
        
    except Exception as e:
        logger.error(f"Error deleting own post: {str(e)}")
        return error_response(
            message="Lỗi xóa bài viết",
            error_code="INTERNAL_ERROR",
            status_code=500
        )


# ==================== END OF POSTS ROUTES ====================
