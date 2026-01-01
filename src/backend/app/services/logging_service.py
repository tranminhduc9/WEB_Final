"""
Logging Service

Module này cung cấp các helper functions để log:
- Activity logs: Hoạt động của user (login, register, update profile, etc.)
- Visit logs: Lượt truy cập địa điểm/bài viết

Author: System
Date: 2024-12-31
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.utils.timezone_helper import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from fastapi import Request

from config.database import ActivityLog, VisitLog, User, Place

logger = logging.getLogger(__name__)


# ==================== HELPER FUNCTIONS ====================

def get_client_ip(request: Request) -> str:
    """
    Lấy IP address của client từ request
    
    Hỗ trợ các trường hợp:
    - Direct connection
    - Behind proxy (X-Forwarded-For)
    - Behind load balancer (X-Real-IP)
    """
    # Check X-Forwarded-For header (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For có thể chứa nhiều IP, lấy IP đầu tiên (client gốc)
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Lấy User-Agent từ request headers"""
    return request.headers.get("User-Agent", "unknown")


# ==================== ACTIVITY LOGGING ====================

async def log_activity(
    db: Session,
    user_id: int,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    request: Optional[Request] = None
) -> Optional[int]:
    """
    Log hoạt động của user vào bảng activity_logs
    
    Args:
        db: Database session
        user_id: ID của user thực hiện action
        action: Loại action (login, register, profile_update, etc.)
        details: Chi tiết bổ sung (optional)
        ip_address: IP address (optional, sẽ lấy từ request nếu có)
        request: FastAPI Request object (optional)
        
    Returns:
        int: ID của activity log record, None nếu lỗi
        
    Actions được hỗ trợ:
        - login: Đăng nhập thành công
        - logout: Đăng xuất
        - register: Đăng ký tài khoản mới
        - password_change: Đổi mật khẩu
        - password_reset: Reset mật khẩu
        - profile_update: Cập nhật thông tin profile
        - avatar_update: Thay đổi avatar
        - favorite_place: Thêm địa điểm yêu thích
        - unfavorite_place: Bỏ địa điểm yêu thích
        - favorite_post: Thêm bài viết yêu thích
        - unfavorite_post: Bỏ bài viết yêu thích
        - create_post: Tạo bài viết mới
        - create_comment: Tạo comment
        - like_post: Like bài viết
        - unlike_post: Unlike bài viết
        - report_content: Báo cáo nội dung vi phạm
    """
    try:
        # Lấy IP từ request nếu không được cung cấp
        if not ip_address and request:
            ip_address = get_client_ip(request)
        
        # Tạo activity log record
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            created_at=utc_now()
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        logger.debug(f"Activity logged: user={user_id}, action={action}")
        return activity.id
        
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        db.rollback()
        return None


def log_activity_sync(
    db: Session,
    user_id: int,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Optional[int]:
    """
    Synchronous version của log_activity
    Sử dụng khi không cần async
    """
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            created_at=utc_now()
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        logger.debug(f"Activity logged (sync): user={user_id}, action={action}")
        return activity.id
        
    except Exception as e:
        logger.error(f"Error logging activity (sync): {str(e)}")
        db.rollback()
        return None


# ==================== VISIT LOGGING ====================

async def log_visit(
    db: Session,
    request: Request,
    user_id: Optional[int] = None,
    place_id: Optional[int] = None,
    post_id: Optional[str] = None,
    page_url: Optional[str] = None
) -> Optional[int]:
    """
    Log lượt truy cập vào bảng visit_logs
    
    Args:
        db: Database session
        request: FastAPI Request object
        user_id: ID của user (None nếu guest)
        place_id: ID địa điểm được xem (optional)
        post_id: ID bài viết được xem (optional)
        page_url: URL trang được truy cập (optional)
        
    Returns:
        int: ID của visit log record, None nếu lỗi
    """
    try:
        # Lấy thông tin từ request
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Lấy page_url từ request nếu không được cung cấp
        if not page_url:
            page_url = str(request.url)
        
        # Tạo visit log record
        visit = VisitLog(
            user_id=user_id,
            place_id=place_id,
            post_id=post_id,
            page_url=page_url,
            ip_address=ip_address,
            user_agent=user_agent,
            visited_at=utc_now()
        )
        
        db.add(visit)
        db.commit()
        db.refresh(visit)
        
        logger.debug(f"Visit logged: place={place_id}, post={post_id}, user={user_id}")
        return visit.id
        
    except Exception as e:
        logger.error(f"Error logging visit: {str(e)}")
        db.rollback()
        return None


# ==================== QUERY FUNCTIONS ====================

def get_user_activities(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    action_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lấy lịch sử hoạt động của user
    
    Args:
        db: Database session
        user_id: ID của user
        limit: Số records tối đa
        offset: Offset cho pagination
        action_filter: Filter theo action type
        
    Returns:
        Dict với logs và metadata
    """
    try:
        query = db.query(ActivityLog).filter(ActivityLog.user_id == user_id)
        
        if action_filter:
            query = query.filter(ActivityLog.action == action_filter)
        
        total = query.count()
        
        activities = query.order_by(desc(ActivityLog.created_at))\
                         .offset(offset)\
                         .limit(limit)\
                         .all()
        
        return {
            "success": True,
            "total": total,
            "logs": [
                {
                    "id": a.id,
                    "action": a.action,
                    "details": a.details,
                    "ip_address": a.ip_address,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in activities
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user activities: {str(e)}")
        return {"success": False, "error": str(e), "logs": []}


def get_place_visits(
    db: Session,
    place_id: int,
    limit: int = 50,
    offset: int = 0,
    days: int = 30
) -> Dict[str, Any]:
    """
    Lấy lịch sử truy cập của địa điểm
    
    Args:
        db: Database session
        place_id: ID địa điểm
        limit: Số records tối đa
        offset: Offset cho pagination
        days: Số ngày gần đây
        
    Returns:
        Dict với visits và metadata
    """
    try:
        since_date = utc_now() - timedelta(days=days)
        
        query = db.query(VisitLog).filter(
            VisitLog.place_id == place_id,
            VisitLog.visited_at >= since_date
        )
        
        total = query.count()
        
        visits = query.order_by(desc(VisitLog.visited_at))\
                     .offset(offset)\
                     .limit(limit)\
                     .all()
        
        return {
            "success": True,
            "total": total,
            "place_id": place_id,
            "days": days,
            "visits": [
                {
                    "id": v.id,
                    "user_id": v.user_id,
                    "ip_address": v.ip_address,
                    "visited_at": v.visited_at.isoformat() if v.visited_at else None
                }
                for v in visits
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting place visits: {str(e)}")
        return {"success": False, "error": str(e), "visits": []}


def get_post_visits(
    db: Session,
    post_id: str,
    limit: int = 50,
    offset: int = 0,
    days: int = 30
) -> Dict[str, Any]:
    """
    Lấy lịch sử truy cập của bài viết
    """
    try:
        since_date = utc_now() - timedelta(days=days)
        
        query = db.query(VisitLog).filter(
            VisitLog.post_id == post_id,
            VisitLog.visited_at >= since_date
        )
        
        total = query.count()
        
        visits = query.order_by(desc(VisitLog.visited_at))\
                     .offset(offset)\
                     .limit(limit)\
                     .all()
        
        return {
            "success": True,
            "total": total,
            "post_id": post_id,
            "days": days,
            "visits": [
                {
                    "id": v.id,
                    "user_id": v.user_id,
                    "ip_address": v.ip_address,
                    "visited_at": v.visited_at.isoformat() if v.visited_at else None
                }
                for v in visits
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting post visits: {str(e)}")
        return {"success": False, "error": str(e), "visits": []}


# ==================== ANALYTICS ====================

def get_visit_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
    """
    Lấy thống kê truy cập tổng hợp
    
    Args:
        db: Database session
        days: Số ngày gần đây để thống kê
        
    Returns:
        Dict với các thống kê
    """
    try:
        since_date = utc_now() - timedelta(days=days)
        
        # Tổng visits
        total_visits = db.query(VisitLog).filter(
            VisitLog.visited_at >= since_date
        ).count()
        
        # Unique visitors (theo IP)
        unique_visitors = db.query(func.count(func.distinct(VisitLog.ip_address))).filter(
            VisitLog.visited_at >= since_date
        ).scalar() or 0
        
        # Logged-in visitors
        logged_in_visitors = db.query(func.count(func.distinct(VisitLog.user_id))).filter(
            VisitLog.visited_at >= since_date,
            VisitLog.user_id.isnot(None)
        ).scalar() or 0
        
        # Top places (by visits)
        top_places = db.query(
            VisitLog.place_id,
            func.count(VisitLog.id).label('visit_count')
        ).filter(
            VisitLog.visited_at >= since_date,
            VisitLog.place_id.isnot(None)
        ).group_by(VisitLog.place_id)\
         .order_by(desc('visit_count'))\
         .limit(10)\
         .all()
        
        # Get place names
        top_places_data = []
        for place_id, visit_count in top_places:
            place = db.query(Place).filter(Place.id == place_id).first()
            top_places_data.append({
                "place_id": place_id,
                "place_name": place.name if place else "Unknown",
                "visit_count": visit_count
            })
        
        # Top posts (by visits)
        top_posts = db.query(
            VisitLog.post_id,
            func.count(VisitLog.id).label('visit_count')
        ).filter(
            VisitLog.visited_at >= since_date,
            VisitLog.post_id.isnot(None)
        ).group_by(VisitLog.post_id)\
         .order_by(desc('visit_count'))\
         .limit(10)\
         .all()
        
        top_posts_data = [
            {"post_id": post_id, "visit_count": visit_count}
            for post_id, visit_count in top_posts
        ]
        
        # Visits per day
        visits_per_day = db.query(
            func.date(VisitLog.visited_at).label('date'),
            func.count(VisitLog.id).label('count')
        ).filter(
            VisitLog.visited_at >= since_date
        ).group_by(func.date(VisitLog.visited_at))\
         .order_by('date')\
         .all()
        
        visits_trend = [
            {"date": str(date), "count": count}
            for date, count in visits_per_day
        ]
        
        return {
            "success": True,
            "period_days": days,
            "summary": {
                "total_visits": total_visits,
                "unique_visitors": unique_visitors,
                "logged_in_visitors": logged_in_visitors
            },
            "top_places": top_places_data,
            "top_posts": top_posts_data,
            "visits_trend": visits_trend
        }
        
    except Exception as e:
        logger.error(f"Error getting visit analytics: {str(e)}")
        return {"success": False, "error": str(e)}


def get_activity_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
    """
    Lấy thống kê hoạt động tổng hợp
    """
    try:
        since_date = utc_now() - timedelta(days=days)
        
        # Activities per action type
        activities_by_type = db.query(
            ActivityLog.action,
            func.count(ActivityLog.id).label('count')
        ).filter(
            ActivityLog.created_at >= since_date
        ).group_by(ActivityLog.action)\
         .order_by(desc('count'))\
         .all()
        
        activities_breakdown = [
            {"action": action, "count": count}
            for action, count in activities_by_type
        ]
        
        # Most active users
        active_users = db.query(
            ActivityLog.user_id,
            func.count(ActivityLog.id).label('activity_count')
        ).filter(
            ActivityLog.created_at >= since_date
        ).group_by(ActivityLog.user_id)\
         .order_by(desc('activity_count'))\
         .limit(10)\
         .all()
        
        active_users_data = []
        for user_id, activity_count in active_users:
            user = db.query(User).filter(User.id == user_id).first()
            active_users_data.append({
                "user_id": user_id,
                "full_name": user.full_name if user else "Unknown",
                "activity_count": activity_count
            })
        
        # Logins today
        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        logins_today = db.query(ActivityLog).filter(
            ActivityLog.action == "login",
            ActivityLog.created_at >= today_start
        ).count()
        
        # New registrations this period
        new_registrations = db.query(ActivityLog).filter(
            ActivityLog.action == "register",
            ActivityLog.created_at >= since_date
        ).count()
        
        return {
            "success": True,
            "period_days": days,
            "summary": {
                "logins_today": logins_today,
                "new_registrations": new_registrations
            },
            "activities_breakdown": activities_breakdown,
            "most_active_users": active_users_data
        }
        
    except Exception as e:
        logger.error(f"Error getting activity analytics: {str(e)}")
        return {"success": False, "error": str(e)}
