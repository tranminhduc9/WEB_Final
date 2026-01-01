"""
System Logs API Routes

Endpoint để xem và quản lý logs hệ thống
"""

from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from typing import Optional
from pathlib import Path
import logging

from middleware.response import success_response, error_response
from config.database import get_db, ActivityLog
from sqlalchemy.orm import Session
from sqlalchemy import desc

logger = logging.getLogger(__name__)

# Tạo router
router = APIRouter(prefix="/logs", tags=["System Logs"])


async def require_admin(request: Request):
    """
    Dependency để kiểm tra admin role
    """
    from middleware.auth import auth_middleware

    user = await auth_middleware.get_current_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để tiếp tục"
        )

    user_role = user.get("role", "user")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập"
        )

    return user


@router.get("/audit", summary="Get Audit Logs")
async def get_audit_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Số lượng log entries"),
    offset: int = Query(0, ge=0, description="Offset để pagination"),
    user_id: Optional[int] = Query(None, description="Filter theo user ID"),
    action_type: Optional[str] = Query(None, description="Filter theo action type"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lấy audit logs từ database

    Yêu cầu: Admin role

    Args:
        limit: Số lượng entries tối đa
        offset: Số entries bỏ qua
        user_id: Filter theo user ID (xem hoạt động của 1 user cụ thể)
        action_type: Filter theo loại action (login, register, etc.)
        current_user: Current admin user

    Returns:
        Danh sách audit log entries
    """
    try:
        from config.database import User
        
        # Query database
        query = db.query(ActivityLog)

        # Filter by user_id
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        
        # Filter by action_type
        if action_type:
            query = query.filter(ActivityLog.action == action_type)

        # Count total
        total = query.count()

        # Sort and Paging
        logs = query.order_by(desc(ActivityLog.created_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

        # Format output with user info
        result_logs = []
        for log in logs:
            # Get user info
            user_info = None
            if log.user_id:
                user = db.query(User).filter(User.id == log.user_id).first()
                if user:
                    user_info = {
                        "id": user.id,
                        "full_name": user.full_name,
                        "email": user.email
                    }
            
            result_logs.append({
                "id": log.id,
                "user_id": log.user_id,
                "user": user_info,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })

        return success_response(
            message=f"Retrieved {len(result_logs)} audit logs",
            data={
                "logs": result_logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )

    except Exception as e:
        logger.error(f"Error reading audit logs: {str(e)}")
        return error_response(
            message=f"Error reading audit logs: {str(e)}",
            error_code="LOG_READ_ERROR"
        )


@router.get("/app", summary="Get Application Logs")
async def get_app_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level: Optional[str] = Query(None, description="Filter theo level (INFO, WARNING, ERROR)"),
    current_user: dict = Depends(require_admin)
):
    """
    Lấy application logs từ file

    Yêu cầu: Admin role

    Args:
        limit: Số lượng lines tối đa
        offset: Số lines bỏ qua
        level: Filter theo log level
        current_user: Current admin user

    Returns:
        Danh sách application log lines
    """
    try:
        # Đường dẫn đến app log file
        backend_dir = Path(__file__).parent.parent.parent.absolute()
        app_log_path = backend_dir / "logs" / "app.log"

        if not app_log_path.exists():
            return success_response(
                message="Application log file not found",
                data={"logs": [], "total": 0}
            )

        # Đọc logs từ file
        logs = []
        with open(app_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                log_line = line.strip()

                # Filter theo level nếu có
                if level and level.upper() not in log_line:
                    continue

                logs.append(log_line)

        # Reverse để hiển thị logs mới nhất trước
        logs = list(reversed(logs))

        # Pagination
        total = len(logs)
        paginated_logs = logs[offset:offset + limit]

        return success_response(
            message=f"Retrieved {len(paginated_logs)} application logs",
            data={
                "logs": paginated_logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )

    except Exception as e:
        logger.error(f"Error reading application logs: {str(e)}")
        return error_response(
            message=f"Error reading application logs: {str(e)}",
            error_code="LOG_READ_ERROR"
        )


@router.get("/stats", summary="Get Logging Statistics")
async def get_logging_stats(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Lấy thống kê về logs

    Yêu cầu: Admin role

    Returns:
        Thống kê về audit logs, application logs
    """
    try:
        backend_dir = Path(__file__).parent.parent.parent.absolute()
        logs_dir = backend_dir / "logs"

        stats = {
            "log_directory": str(logs_dir),
            "log_directory_exists": logs_dir.exists(),
            "files": []
        }

        if logs_dir.exists():
            # Lấy thông tin các log files
            for log_file in logs_dir.glob("*.log"):
                file_stat = log_file.stat()
                stats["files"].append({
                    "name": log_file.name,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": file_stat.st_mtime
                })

        return success_response(
            message="Logging statistics retrieved",
            data=stats
        )

    except Exception as e:
        logger.error(f"Error getting logging stats: {str(e)}")
        return error_response(
            message=f"Error getting logging stats: {str(e)}",
            error_code="STATS_ERROR"
        )


@router.get("/visits", summary="Get Visit Logs")
async def get_visit_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Số lượng log entries"),
    offset: int = Query(0, ge=0, description="Offset để pagination"),
    user_id: Optional[int] = Query(None, description="Filter theo user ID"),
    place_id: Optional[int] = Query(None, description="Filter theo place ID"),
    post_id: Optional[str] = Query(None, description="Filter theo post ID"),
    days: int = Query(30, ge=1, le=365, description="Số ngày gần đây"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lấy visit logs

    Yêu cầu: Admin role

    Args:
        limit: Số lượng entries tối đa
        offset: Số entries bỏ qua
        user_id: Filter theo user ID (xem lịch sử truy cập của 1 user)
        place_id: Filter theo địa điểm (optional)
        post_id: Filter theo bài viết (optional)
        days: Số ngày gần đây
        current_user: Current admin user

    Returns:
        Danh sách visit log entries
    """
    try:
        from config.database import VisitLog, Place, User
        from datetime import datetime, timedelta
        
        from app.utils.timezone_helper import utc_now
        since_date = utc_now() - timedelta(days=days)
        
        # Query database
        query = db.query(VisitLog).filter(VisitLog.visited_at >= since_date)

        # Filter by user_id
        if user_id:
            query = query.filter(VisitLog.user_id == user_id)
        
        # Filter by place_id
        if place_id:
            query = query.filter(VisitLog.place_id == place_id)
        
        # Filter by post_id
        if post_id:
            query = query.filter(VisitLog.post_id == post_id)

        # Count total
        total = query.count()

        # Sort and Paging
        logs = query.order_by(desc(VisitLog.visited_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

        # Format output with user info
        result_logs = []
        for log in logs:
            # Get place name if available
            place_name = None
            if log.place_id:
                place = db.query(Place).filter(Place.id == log.place_id).first()
                place_name = place.name if place else None
            
            # Get user info if available
            user_info = None
            if log.user_id:
                user = db.query(User).filter(User.id == log.user_id).first()
                if user:
                    user_info = {
                        "id": user.id,
                        "full_name": user.full_name,
                        "email": user.email
                    }
            
            result_logs.append({
                "id": log.id,
                "user_id": log.user_id,
                "user": user_info,
                "place_id": log.place_id,
                "place_name": place_name,
                "post_id": log.post_id,
                "page_url": log.page_url,
                "ip_address": log.ip_address,
                "visited_at": log.visited_at.isoformat() if log.visited_at else None
            })

        return success_response(
            message=f"Retrieved {len(result_logs)} visit logs",
            data={
                "logs": result_logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "days": days
            }
        )

    except Exception as e:
        logger.error(f"Error reading visit logs: {str(e)}")
        return error_response(
            message=f"Error reading visit logs: {str(e)}",
            error_code="LOG_READ_ERROR"
        )


@router.get("/analytics", summary="Get Analytics Summary")
async def get_analytics_summary(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Số ngày gần đây"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê tổng hợp cho admin dashboard

    Yêu cầu: Admin role

    Args:
        days: Số ngày gần đây để thống kê
        current_user: Current admin user

    Returns:
        Thống kê visits, activities, top places, active users
    """
    try:
        from app.services.logging_service import get_visit_analytics, get_activity_analytics
        
        # Get analytics data
        visit_analytics = get_visit_analytics(db, days)
        activity_analytics = get_activity_analytics(db, days)
        
        return success_response(
            message="Analytics retrieved successfully",
            data={
                "visits": visit_analytics,
                "activities": activity_analytics
            }
        )

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return error_response(
            message=f"Error getting analytics: {str(e)}",
            error_code="ANALYTICS_ERROR"
        )

