"""
Middleware Audit Logging - Ghi log hoạt động hệ thống

Module này cung cấp chức năng logging thống nhất cho mọi hoạt động,
giúp tracking và debug hệ thống hiệu quả.
Format log nhất quán qua mọi phiên bản.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
import os
from enum import Enum
from sqlalchemy.orm import Session
from config.database import SessionLocal, ActivityLog

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Các mức độ logging"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ActionType(Enum):
    """Các loại hành động cần log"""
    # Authentication
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    LOGIN = "auth_login"
    LOGOUT = "auth_logout"
    REGISTER = "auth_register"
    PASSWORD_CHANGE = "auth_password_change"
    PASSWORD_RESET = "auth_password_reset"

    # User actions
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    PROFILE_UPDATE = "profile_update"

    # Content actions
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    POST_CREATE = "post_create"
    POST_UPDATE = "post_update"
    POST_DELETE = "post_delete"
    POST_LIKE = "post_like"
    POST_UNLIKE = "post_unlike"
    COMMENT_CREATE = "comment_create"
    COMMENT_DELETE = "comment_delete"

    # Favorites
    FAVORITE_ADD = "favorite_add"
    FAVORITE_REMOVE = "favorite_remove"

    # System actions
    UPLOAD_FILE = "upload_file"
    API_CALL = "api_call"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"

    # Data access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"


class AuditLogEntry:
    """
    Đối tượng đại diện cho một log entry
    """

    def __init__(
        self,
        action_type: ActionType,
        message: str,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None
    ):
        """
        Khởi tạo audit log entry

        Args:
            action_type: Loại hành động
            message: Message mô tả
            level: Mức độ log
            user_id: ID người dùng thực hiện
            ip_address: IP address của client
            user_agent: User agent string
            request_id: ID duy nhất của request
            details: Chi tiết bổ sung
            status_code: HTTP status code
            response_time: Thời gian xử lý (ms)
        """
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        # Handle both enum and string values
        self.action_type = action_type.value if hasattr(action_type, 'value') else action_type
        self.message = message
        # Handle both enum and string values
        self.level = level.value if hasattr(level, 'value') else level
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_id = request_id
        self.details = details or {}
        self.status_code = status_code
        self.response_time = response_time

    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi thành dictionary

        Returns:
            Dict: Log entry as dict
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type,
            "message": self.message,
            "level": self.level,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "details": self.details,
            "status_code": self.status_code,
            "response_time": self.response_time
        }

    def to_json(self) -> str:
        """
        Chuyển đổi thành JSON string

        Returns:
            str: JSON representation
        """
        return json.dumps(self.to_dict(), default=str)


class AuditConfig:
    """Configuration class for audit logging"""
    def __init__(self):
        self.log_file = None
        self.buffer_size = 100
        self.format = "json"
        self.rotate_logs = True
        self.max_file_size = 10 * 1024 * 1024  # 10MB


class AuditLogger:
    """
    Logger chính cho audit logging

    Cung cấp các method để log các loại hành động khác nhau.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Khởi tạo audit logger

        Args:
            log_file: Path đến file log (optional)
        """
        self.config = AuditConfig()
        # Set default log file if not provided
        self.log_file = log_file or os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
        self.buffer = []
        self.setup_file_logger()

    def setup_file_logger(self):
        """Setup file logger nếu có log_file"""
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)

    def log_action(
        self,
        action_type: ActionType,
        message: str,
        level: LogLevel = LogLevel.INFO,
        request: Optional[Request] = None,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None
    ) -> AuditLogEntry:
        """
        Log một hành động

        Args:
            action_type: Loại hành động
            message: Message mô tả
            level: Mức độ log
            request: FastAPI request object
            user_id: ID người dùng
            details: Chi tiết bổ sung
            status_code: HTTP status code
            response_time: Thời gian xử lý

        Returns:
            AuditLogEntry: Entry đã được log
        """
        # Lấy thông tin từ request nếu có
        ip_address = self._get_ip_address(request) if request else None
        user_agent = self._get_user_agent(request) if request else None
        request_id = self._get_request_id(request) if request else None

        # Lấy user_id từ request nếu không được cung cấp
        if not user_id and request:
            user_id = self._get_user_id_from_request(request)

        # Tạo log entry
        entry = AuditLogEntry(
            action_type=action_type,
            message=message,
            level=level,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details,
            status_code=status_code,
            response_time=response_time
        )

        # Log ra console/file
        log_message = f"[{entry.action_type}] {entry.message}"
        if entry.user_id:
            log_message += f" | User: {entry.user_id}"
        if entry.ip_address:
            log_message += f" | IP: {entry.ip_address}"
        if entry.response_time:
            log_message += f" | Time: {entry.response_time:.2f}ms"

        # Ghi log theo level
        if entry.level == LogLevel.DEBUG.value:
            logger.debug(log_message)
        elif entry.level == LogLevel.INFO.value:
            logger.info(log_message)
        elif entry.level == LogLevel.WARNING.value:
            logger.warning(log_message)
        elif entry.level == LogLevel.ERROR.value:
            logger.error(log_message)
        elif entry.level == LogLevel.CRITICAL.value:
            logger.critical(log_message)

        # Ghi ra file nếu được cấu hình
        if self.log_file:
            if self.config.buffer_size > 0:
                self._add_to_buffer(entry)
            else:
                self._write_to_file(entry)

        # Ghi vào Database (Activity Logs) nếu có user_id
        if entry.user_id:
            try:
                db = SessionLocal()
                # Chỉ log short details vào column details (text)
                detail_text = entry.message
                if entry.details:
                    # Kèm thêm một số info quan trọng
                    detail_text += f" | {json.dumps(entry.details, default=str)}"
                
                # Truncate nếu quá dài
                if len(detail_text) > 2000:
                    detail_text = detail_text[:2000] + "..."

                activity_log = ActivityLog(
                    user_id=int(entry.user_id),
                    action=entry.action_type if isinstance(entry.action_type, str) else str(entry.action_type),
                    details=detail_text,
                    ip_address=entry.ip_address,
                    created_at=entry.timestamp
                )
                db.add(activity_log)
                db.commit()
                db.close()
            except Exception as e:
                logger.error(f"Failed to write to activity_logs table: {e}")
                # Không raise error để tránh ảnh hưởng request chính

        return entry

    def log_authentication(
        self,
        action: str,
        email: str,
        success: bool,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log các hành động authentication theo API contract

        Actions quan trọng cần log: Login, Delete, Update

        Args:
            action: Loại hành động (login, logout, register, etc.)
            email: Email người dùng
            success: Có thành công không
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        action_type = {
            "login": ActionType.LOGIN,
            "logout": ActionType.LOGOUT,
            "register": ActionType.REGISTER,
            "password_change": ActionType.PASSWORD_CHANGE,
            "password_reset": ActionType.PASSWORD_RESET,
            "forgot_password": ActionType.PASSWORD_RESET,
            "refresh_token": ActionType.LOGIN
        }.get(action, ActionType.LOGIN)

        level = LogLevel.INFO if success else LogLevel.WARNING
        message = f"Authentication {action} {'success' if success else 'failed'} for {email}"

        if details is None:
            details = {}
        details["email"] = email
        details["success"] = success
        details["action"] = action

        self.log_action(
            action_type=action_type,
            message=message,
            level=level,
            request=request,
            details=details
        )

    def log_content_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log các hành động quan trọng trên content theo API contract

        Actions quan trọng: Delete, Update (tự động ghi vào activity_logs)

        Args:
            action: Loại hành động (create, update, delete, like, comment)
            resource_type: Loại resource (post, review, user, place)
            resource_id: ID của resource
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        action_mapping = {
            "create": ActionType.DATA_CREATE,
            "update": ActionType.DATA_UPDATE,
            "delete": ActionType.DATA_DELETE,
            "like": ActionType.POST_LIKE,
            "unlike": ActionType.POST_UNLIKE,
            "comment": ActionType.COMMENT_CREATE,
            "favorite_add": ActionType.FAVORITE_ADD,
            "favorite_remove": ActionType.FAVORITE_REMOVE
        }

        action_type = action_mapping.get(action, ActionType.DATA_WRITE)

        # Đánh mức độ log cao hơn cho các action quan trọng
        level = LogLevel.INFO
        if action in ["delete", "update"]:
            level = LogLevel.WARNING  # Actions quan trọng cần theo dõi

        message = f"Content {action}: {resource_type}"
        if resource_id:
            message += f" (ID: {resource_id})"

        if details is None:
            details = {}
        details.update({
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "important_action": action in ["delete", "update"]  # Đánh dấu cho activity_logs
        })

        self.log_action(
            action_type=action_type,
            message=message,
            level=level,
            request=request,
            details=details
        )

    def log_admin_action(
        self,
        action: str,
        target_type: str,
        target_id: Optional[str] = None,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log các hành động admin theo API contract

        Args:
            action: Loại hành động (block_user, delete_post, etc.)
            target_type: Loại target (user, post, place)
            target_id: ID của target
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        # Admin actions luôn là level cao để giám sát
        level = LogLevel.WARNING
        message = f"Admin {action}: {target_type}"
        if target_id:
            message += f" (ID: {target_id})"

        if details is None:
            details = {}
        details.update({
            "admin_action": True,
            "target_type": target_type,
            "target_id": target_id,
            "action": action
        })

        self.log_action(
            action_type=ActionType.DATA_DELETE if "delete" in action else ActionType.DATA_UPDATE,
            message=message,
            level=level,
            request=request,
            details=details
        )

    def log_data_access(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log các hành động truy cập dữ liệu

        Args:
            action: Loại hành động (read, write, delete)
            resource_type: Loại resource (user, post, place, etc.)
            resource_id: ID của resource
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        action_type = {
            "read": ActionType.DATA_READ,
            "write": ActionType.DATA_WRITE,
            "delete": ActionType.DATA_DELETE
        }.get(action, ActionType.DATA_READ)

        message = f"Data {action}: {resource_type}"
        if resource_id:
            message += f" (ID: {resource_id})"

        if details is None:
            details = {}
        details["resource_type"] = resource_type
        details["resource_id"] = resource_id

        self.log_action(
            action_type=action_type,
            message=message,
            request=request,
            details=details
        )

    def log_error(
        self,
        error: Exception,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log errors

        Args:
            error: Exception object
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        message = f"Error occurred: {str(error)}"

        if details is None:
            details = {}
        details["error_type"] = type(error).__name__
        details["error_message"] = str(error)
        details["traceback"] = traceback.format_exc()

        self.log_action(
            action_type=ActionType.SYSTEM_ERROR,
            message=message,
            level=LogLevel.ERROR,
            request=request,
            details=details
        )

    def log_security_event(
        self,
        event_type: str,
        message: str,
        request: Optional[Request] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log security events

        Args:
            event_type: Loại sự kiện (rate_limit, unauthorized, etc.)
            message: Message mô tả
            request: FastAPI request
            details: Chi tiết bổ sung
        """
        if details is None:
            details = {}
        details["security_event_type"] = event_type

        self.log_action(
            action_type=ActionType.SECURITY_ALERT,
            message=f"Security Event - {message}",
            level=LogLevel.WARNING,
            request=request,
            details=details
        )

    def _get_ip_address(self, request: Request) -> Optional[str]:
        """Lấy IP address từ request"""
        # Check various headers for real IP
        headers = [
            "X-Forwarded-For",
            "X-Real-IP",
            "X-Client-IP",
            "CF-Connecting-IP",  # Cloudflare
            "True-Client-IP"
        ]

        for header in headers:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For có thể chứa nhiều IPs
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                return ip

        return request.client.host if request.client else None

    def _get_user_agent(self, request: Request) -> Optional[str]:
        """Lấy User-Agent từ request"""
        return request.headers.get("User-Agent")

    def _get_request_id(self, request: Request) -> Optional[str]:
        """Lấy Request ID từ request headers hoặc tạo mới"""
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            # Tạo request ID và lưu vào request state
            request_id = str(uuid.uuid4())
            if not hasattr(request.state, "request_id"):
                request.state.request_id = request_id
        return request_id

    def _get_user_id_from_request(self, request: Request) -> Optional[str]:
        """Lấy user ID từ request state"""
        if hasattr(request.state, 'user') and request.state.user:
            return request.state.user.get('user_id')
        return None

    def _write_to_file(self, entry: AuditLogEntry):
        """Ghi log entry vào file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json() + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log to file: {str(e)}")

    def _add_to_buffer(self, entry: AuditLogEntry):
        """Add entry to buffer"""
        self.buffer.append(entry)

        # Flush buffer if it exceeds buffer size
        if len(self.buffer) >= self.config.buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        """Flush buffer to file"""
        if not self.buffer or not self.log_file:
            return

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                for entry in self.buffer:
                    f.write(entry.to_json() + '\n')
            self.buffer.clear()
        except Exception as e:
            logger.error(f"Failed to flush audit log buffer: {str(e)}")


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware để tự động log tất cả requests

    Tự động log request/response cho mục đích audit.
    """

    def __init__(self, app, audit_logger: AuditLogger):
        """
        Khởi tạo middleware

        Args:
            app: FastAPI application
            audit_logger: Audit logger instance
        """
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và log

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response với log đã được ghi
        """
        start_time = time.time()

        # Tạo request ID nếu chưa có
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid.uuid4())

        # Log request bắt đầu
        self._log_request_start(request)

        try:
            # Process request
            response = await call_next(request)

            # Tính response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log request hoàn thành
            self._log_request_complete(request, response, response_time)

            return response

        except Exception as e:
            # Tính response time
            response_time = (time.time() - start_time) * 1000

            # Log error
            self.audit_logger.log_error(
                error=e,
                request=request,
                details={
                    "response_time": response_time,
                    "method": request.method,
                    "url": str(request.url)
                }
            )

            raise

    def _log_request_start(self, request: Request):
        """Log khi request bắt đầu"""
        self.audit_logger.log_action(
            action_type=ActionType.API_CALL,
            message=f"Request started: {request.method} {request.url.path}",
            level=LogLevel.DEBUG,
            request=request,
            details={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "content_type": request.headers.get("Content-Type")
            }
        )

    def _log_request_complete(self, request: Request, response: Response, response_time: float):
        """Log khi request hoàn thành"""
        # Xác định level based on status code
        if response.status_code >= 500:
            level = LogLevel.ERROR
        elif response.status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO

        self.audit_logger.log_action(
            action_type=ActionType.API_CALL,
            message=f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            level=level,
            request=request,
            status_code=response.status_code,
            response_time=response_time,
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "content_length": response.headers.get("Content-Length")
            }
        )


# Global audit logger instance
audit_logger = AuditLogger()


# Decorator cho audit logging
def audit_action(action_type: ActionType, level: LogLevel = LogLevel.INFO, message: Optional[str] = None):
    """
    Decorator để auto log cho functions

    Args:
        action_type: Loại hành động
        level: Mức độ log
        message: Message mô tả (optional)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Lấy request từ kwargs nếu có
            request = kwargs.get('request')
            user_id = kwargs.get('user_id')

            # Use provided message or generate from function name
            log_message = message or f"Function {func.__name__} executed"

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Log success
                audit_logger.log_action(
                    action_type=action_type,
                    message=log_message,
                    level=level,
                    request=request,
                    user_id=user_id
                )

                return result

            except Exception as e:
                # Log error
                audit_logger.log_action(
                    action_type=ActionType.SYSTEM_ERROR,
                    message=f"Error in {func.__name__}: {str(e)}",
                    level=LogLevel.ERROR,
                    request=request,
                    user_id=user_id,
                    details={"error": str(e), "function": func.__name__}
                )
                raise

        return wrapper
    return decorator


# Utility functions
def get_user_activity_logs(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Lấy logs hoạt động của user (mock implementation)

    Args:
        user_id: ID của user
        limit: Số logs tối đa

    Returns:
        List: Danh sách logs
    """
    # Trong thực tế, đây là function đọc từ database hoặc log files
    return []


def log_file_upload(user_id: str, file_name: str, file_size: int, request: Request):
    """
    Log khi user upload file

    Args:
        user_id: ID của user
        file_name: Tên file
        file_size: Kích thước file
        request: FastAPI request
    """
    audit_logger.log_action(
        action_type=ActionType.UPLOAD_FILE,
        message=f"File uploaded: {file_name}",
        request=request,
        details={
            "file_name": file_name,
            "file_size": file_size,
            "user_id": user_id
        }
    )


# Add async methods to AuditLogger
async def log_user_action(
    self,
    user_id: str,
    action_type: ActionType,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLogEntry:
    """Log user action asynchronously"""
    return self.log_action(
        action_type=action_type,
        message=f"User action: {action_type.value}",
        user_id=user_id,
        request=request,
        details=details
    )


async def log_security_event(
    self,
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    request: Optional[Request] = None
) -> AuditLogEntry:
    """Log security event asynchronously"""
    level = LogLevel.ERROR if severity == "high" else LogLevel.WARNING
    return self.log_action(
        action_type=ActionType.SECURITY_ALERT,
        message=f"Security event: {event_type}",
        level=level,
        request=request,
        details=details
    )


async def log_api_call(
    self,
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    request: Optional[Request] = None,
    response_time: Optional[float] = None
) -> AuditLogEntry:
    """Log API call asynchronously"""
    return self.log_action(
        action_type=ActionType.API_CALL,
        message=f"{method} {endpoint}",
        user_id=user_id,
        request=request,
        details={"endpoint": endpoint, "method": method},
        response_time=response_time
    )


async def log_system_event(
    self,
    event: str,
    level: LogLevel = LogLevel.INFO,
    details: Optional[Dict[str, Any]] = None
) -> AuditLogEntry:
    """Log system event asynchronously"""
    return self.log_action(
        action_type=ActionType.SYSTEM_ERROR if level == LogLevel.ERROR else ActionType.API_CALL,
        message=f"System event: {event}",
        level=level,
        details=details
    )


# Monkey patch the methods into AuditLogger class
AuditLogger.log_user_action = log_user_action
AuditLogger.log_security_event = log_security_event
AuditLogger.log_api_call = log_api_call
AuditLogger.log_system_event = log_system_event


# Note: audit_logger is already defined above


# Utility functions for tests
async def log_user_action(user_id: str, action_type: ActionType, **kwargs):
    """Global function to log user action"""
    return await audit_logger.log_user_action(user_id, action_type, **kwargs)


async def log_security_event(event_type: str, severity: str, details: Dict[str, Any], **kwargs):
    """Global function to log security event"""
    return await audit_logger.log_security_event(event_type, severity, details, **kwargs)


async def log_api_call(endpoint: str, method: str, **kwargs):
    """Global function to log API call"""
    return await audit_logger.log_api_call(endpoint, method, **kwargs)


async def log_system_event(event: str, **kwargs):
    """Global function to log system event"""
    return await audit_logger.log_system_event(event, **kwargs)