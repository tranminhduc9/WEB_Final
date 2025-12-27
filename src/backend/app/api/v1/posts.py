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
import logging

from config.database import get_db, User, UserPostFavorite, Place
from app.utils.image_helpers import get_main_image_url
from app.utils.place_helpers import get_place_compact, get_user_compact
from middleware.auth import get_current_user, get_optional_user
from middleware.response import success_response, error_response
from middleware.mongodb_client import mongo_client, get_mongodb

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
    
    return {
        "_id": str(post.get("_id")),
        "author": author,
        "title": post.get("title"),
        "content": post.get("content"),
        "rating": post.get("rating"),
        "related_place": related_place,
        "images": post.get("images", []),
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
        
        # Query posts from MongoDB
        posts = await mongo_client.get_posts(limit=limit, skip=skip, sort="newest")
        
        # Count total
        total = await mongo_client.count("posts", {"status": "approved"})
        
        # Format response
        current_user_id = current_user.get("user_id") if current_user else None
        formatted_posts = []
        for post in posts:
            formatted = await format_post_response(post, db, current_user_id)
            formatted_posts.append(formatted)
        
        return success_response(
            message="Lấy danh sách bài viết thành công",
            data=formatted_posts,
            pagination={
                "page": page,
                "limit": limit,
                "total_items": total,
                "total_pages": (total + limit - 1) // limit
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
        
        # Prepare post document
        post_doc = {
            "type": "post",
            "author_id": user_id,
            "title": post_data.title,
            "content": post_data.content,
            "images": post_data.images or [],
            "tags": post_data.tags or [],
            "related_place_id": post_data.related_place_id,
            "rating": post_data.rating,
            "likes_count": 0,
            "comments_count": 0,
            "status": "pending"
        }
        
        # Insert to MongoDB
        post_id = await mongo_client.create_post(post_doc)
        
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
        
        # Get post
        post = await mongo_client.find_one("posts", {"_id": ObjectId(post_id)})
        if not post:
            return error_response(
                message="Bài viết không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        # Format post
        current_user_id = current_user.get("user_id") if current_user else None
        formatted_post = await format_post_response(post, db, current_user_id)
        
        # Get comments (root level)
        comments = await mongo_client.get_root_comments(post_id, limit=20)
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
        
        user_id = current_user.get("user_id")
        
        result = await mongo_client.toggle_like(post_id, user_id)
        
        # Update likes_count in post
        from bson import ObjectId
        await mongo_client.update_one("posts", {"_id": ObjectId(post_id)}, {
            "likes_count": result["total_likes"]
        })
        
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
        
        user_id = current_user.get("user_id")
        
        comment_doc = {
            "post_id": post_id,
            "user_id": user_id,
            "content": comment_data.content,
            "images": comment_data.images or [],
            "parent_id": None  # Root comment
        }
        
        comment_id = await mongo_client.create_comment(comment_doc)
        
        # Update comments_count
        from bson import ObjectId
        post = await mongo_client.find_one("posts", {"_id": ObjectId(post_id)})
        if post:
            await mongo_client.update_one("posts", {"_id": ObjectId(post_id)}, {
                "comments_count": post.get("comments_count", 0) + 1
            })
        
        return success_response(
            message="Thêm comment thành công",
            data={
                "comment_id": comment_id,
                "created_at": datetime.utcnow().isoformat()
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
        
        user_id = current_user.get("user_id")
        
        # Verify parent comment exists
        from bson import ObjectId
        parent = await mongo_client.find_one("post_comments", {"_id": ObjectId(comment_id)})
        if not parent:
            return error_response(
                message="Comment gốc không tồn tại",
                error_code="NOT_FOUND",
                status_code=404
            )
        
        reply_id = await mongo_client.create_reply(
            parent_id=comment_id,
            user_id=user_id,
            content=reply_data.content
        )
        
        # Update comments_count of post
        post_id = parent.get("post_id")
        post = await mongo_client.find_one("posts", {"_id": ObjectId(post_id)})
        if post:
            await mongo_client.update_one("posts", {"_id": ObjectId(post_id)}, {
                "comments_count": post.get("comments_count", 0) + 1
            })
        
        return success_response(
            message="Reply thành công",
            data={
                "comment_id": reply_id,
                "created_at": datetime.utcnow().isoformat()
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
        else:
            favorite = UserPostFavorite(user_id=user_id, post_id=post_id)
            db.add(favorite)
            db.commit()
            is_favorited = True
        
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
        
        report_doc = {
            "target_type": "post",
            "target_id": post_id,
            "reporter_id": user_id,
            "reason": report_data.reason,
            "description": report_data.description
        }
        
        await mongo_client.create_report(report_doc)
        
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
        
        report_doc = {
            "target_type": "comment",
            "target_id": comment_id,
            "reporter_id": user_id,
            "reason": report_data.reason,
            "description": report_data.description
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


# ==================== END OF POSTS ROUTES ====================
