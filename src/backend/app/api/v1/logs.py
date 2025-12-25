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
    action_type: Optional[str] = Query(None, description="Filter theo action type"),
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Lấy audit logs từ file

    Yêu cầu: Admin role

    Args:
        limit: Số lượng entries tối đa
        offset: Số entries bỏ qua
        action_type: Filter theo loại action (login, register, etc.)
        current_user: Current admin user

    Returns:
        Danh sách audit log entries
    """
    try:
        # Query database
        query = db.query(ActivityLog)

        # Filter
        if action_type:
            query = query.filter(ActivityLog.action == action_type)

        # Count total
        total = query.count()

        # Sort and Paging
        logs = query.order_by(desc(ActivityLog.created_at))\
                    .offset(offset)\
                    .limit(limit)\
                    .all()

        # Format output
        result_logs = []
        for log in logs:
            result_logs.append({
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at
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
