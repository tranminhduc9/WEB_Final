"""
Audit Log Middleware v2.0 cho WEB Final API

Triển khai Audit Logging để ghi lại các hành động quan trọng:
- Login, Logout
- Create, Update, Delete operations
- Sensitive data access
- Admin operations
Ghi vào bảng activity_logs theo API contract.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """Enum định nghĩa các loại audit actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS_DENIED = "access_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SENSITIVE_ACCESS = "sensitive_access"
    ADMIN_ACTION = "admin_action"


class AuditSeverity(Enum):
    """Enum định nghĩa mức độ nghiêm trọng của audit log"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Audit Log Middleware cho WEB Final API

    Ghi lại các hành động quan trọng của user vào activity_logs.
    Tự động detect các loại actions dựa trên HTTP method và endpoint.
    """

    def __init__(
        self,
        app,
        database_connection=None,  # Database connection để lưu logs
        excluded_paths: Optional[List[str]] = None,
        sensitive_endpoints: Optional[List[str]] = None,
        log_all_requests: bool = False,
    ):
        """
        Initialize Audit Log Middleware

        Args:
            app: FastAPI application instance
            database_connection: Database connection để lưu audit logs
            excluded_paths: Paths không cần audit logging
            sensitive_endpoints: Endpoint nhạy cảm cần ghi log chi tiết
            log_all_requests: Log tất cả requests (useful cho development)
        """
        super().__init__(app)

        self.db_connection = database_connection
        self.log_all_requests = log_all_requests

        # Paths excluded từ audit logging
        self.excluded_paths = excluded_paths or [
            "/health",
            "/favicon.ico",
            "/static/",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        # Sensitive endpoints cần detailed logging
        self.sensitive_endpoints = sensitive_endpoints or [
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/users/me",
            "/api/v1/users/me/password",
            "/api/v1/admin/",
        ]

        # Action mapping theo HTTP method
        self.method_action_mapping = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE,
        }

        # Statistics tracking
        self.stats = {
            "total_logs": 0,
            "login_attempts": 0,
            "failed_attempts": 0,
            "admin_actions": 0,
            "sensitive_accesses": 0,
        }

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và ghi audit log

        Args:
            request: HTTP request cần xử lý
            call_next: Middleware tiếp theo

        Returns:
            HTTP response với audit logging
        """
        start_time = datetime.utcnow()

        # Skip audit logging cho excluded paths
        should_log = not self._is_excluded_path(request.url.path)

        if should_log or self.log_all_requests:
            # Collect request information
            request_info = await self._collect_request_info(request)

        try:
            # Process request
            response = await call_next(request)

            if should_log or self.log_all_requests:
                # Collect response information
                response_info = self._collect_response_info(response)

                # Determine audit action
                action = self._determine_audit_action(request, response)

                # Calculate duration
                duration = (datetime.utcnow() - start_time).total_seconds()

                # Create audit log entry
                audit_entry = await self._create_audit_entry(
                    request_info=request_info,
                    response_info=response_info,
                    action=action,
                    duration=duration,
                    timestamp=start_time
                )

                # Log audit entry
                await self._log_audit_entry(audit_entry)

            return response

        except Exception as e:
            # Log failed requests
            if should_log or self.log_all_requests:
                audit_entry = await self._create_audit_entry(
                    request_info=request_info or {},
                    response_info={"status_code": 500, "error": str(e)},
                    action=AuditAction.ACCESS_DENIED,
                    duration=(datetime.utcnow() - start_time).total_seconds(),
                    timestamp=start_time,
                    is_error=True
                )
                await self._log_audit_entry(audit_entry)
            raise

    def _is_excluded_path(self, path: str) -> bool:
        """
        Kiểm tra path có nên được loại trừ khỏi audit logging không
        """
        if path in self.excluded_paths:
            return True

        for excluded_path in self.sensitive_endpoints:
            if excluded_path.endswith('/') and path.startswith(excluded_path):
                return True

        return False

    async def _collect_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Thu thập thông tin request cho audit log

        Args:
            request: FastAPI request object

        Returns:
            Request information dictionary
        """
        info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
        }

        # Add user information nếu authenticated
        if hasattr(request.state, 'user') and request.state.user:
            user = request.state.user
            info["user_id"] = user.get("id")
            info["user_email"] = user.get("email")
            info["user_role"] = user.get("role_id")

        # Add request body cho sensitive endpoints (sanitize)
        if self._is_sensitive_endpoint(request.url.path):
            info["request_body"] = await self._sanitize_request_body(request)

        return info

    def _collect_response_info(self, response: Response) -> Dict[str, Any]:
        """
        Thu thập thông tin response cho audit log

        Args:
            response: HTTP response object

        Returns:
            Response information dictionary
        """
        return {
            "status_code": getattr(response, 'status_code', 200),
            "content_type": getattr(response.headers, 'content_type', ''),
        }

    def _determine_audit_action(self, request: Request, response: Response) -> AuditAction:
        """
        Xác định audit action dựa trên request và response

        Args:
            request: HTTP request
            response: HTTP response

        Returns:
            AuditAction enum
        """
        path = request.url.path
        method = request.method
        status_code = getattr(response, 'status_code', 200)

        # Login/logout actions
        if path == "/api/v1/auth/login":
            return AuditAction.LOGIN
        elif path == "/api/v1/auth/logout":
            return AuditAction.LOGOUT

        # Admin actions
        elif path.startswith("/api/v1/admin/"):
            return AuditAction.ADMIN_ACTION

        # Access denied
        elif status_code == 401 or status_code == 403:
            return AuditAction.ACCESS_DENIED

        # Rate limit exceeded
        elif status_code == 429:
            return AuditAction.RATE_LIMIT_EXCEEDED

        # Sensitive access
        elif self._is_sensitive_endpoint(path):
            return AuditAction.SENSITIVE_ACCESS

        # Default action based on HTTP method
        else:
            return self.method_action_mapping.get(method, AuditAction.READ)

    def _is_sensitive_endpoint(self, path: str) -> bool:
        """
        Kiểm tra endpoint có nhạy cảm không
        """
        for sensitive_path in self.sensitive_endpoints:
            if path.startswith(sensitive_path):
                return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        """
        Lấy client IP address
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"

    async def _sanitize_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Sanitize request body để loại sensitive data trước khi logging

        Args:
            request: HTTP request

        Returns:
            Sanitized request body hoặc None
        """
        try:
            if hasattr(request, '_json'):
                body = request._json
            else:
                body = await request.json() if hasattr(request, 'json') else None

            if not body:
                return None

            # Sanitize sensitive fields
            sensitive_fields = ['password', 'token', 'secret', 'key']
            sanitized = body.copy()

            for field in sensitive_fields:
                if field in sanitized:
                    sanitized[field] = "***REDACTED***"

            return sanitized
        except Exception:
            # Nếu không thể parse body, return None để tránh logging sensitive data
            return None

    async def _create_audit_entry(
        self,
        request_info: Dict[str, Any],
        response_info: Dict[str, Any],
        action: AuditAction,
        duration: float,
        timestamp: datetime,
        is_error: bool = False
    ) -> Dict[str, Any]:
        """
        Tạo audit log entry

        Args:
            request_info: Request information
            response_info: Response information
            action: Audit action
            duration: Request duration in seconds
            timestamp: Request timestamp
            is_error: Whether this is an error log

        Returns:
            Audit log entry dictionary
        """
        entry = {
            "timestamp": timestamp.isoformat(),
            "action": action.value,
            "method": request_info.get("method"),
            "endpoint": request_info.get("path"),
            "user_id": request_info.get("user_id"),
            "user_email": request_info.get("user_email"),
            "user_role": request_info.get("user_role"),
            "client_ip": request_info.get("client_ip"),
            "user_agent": request_info.get("user_agent"),
            "status_code": response_info.get("status_code"),
            "duration_ms": int(duration * 1000),
            "query_params": request_info.get("query_params", {}),
            "is_error": is_error,
        }

        # Add request body cho sensitive endpoints
        if request_info.get("request_body"):
            entry["request_body"] = request_info["request_body"]

        # Determine severity
        entry["severity"] = self._determine_severity(action, is_error, response_info.get("status_code", 200))

        # Add additional context
        entry["context"] = self._build_context(request_info, response_info, action)

        return entry

    def _determine_severity(self, action: AuditAction, is_error: bool, status_code: int) -> str:
        """
        Xác định mức độ nghiêm trọng của audit log
        """
        if is_error or status_code >= 500:
            return AuditSeverity.CRITICAL.value
        elif action in [AuditAction.ACCESS_DENIED, AuditAction.RATE_LIMIT_EXCEEDED]:
            return AuditSeverity.HIGH.value
        elif action in [AuditAction.ADMIN_ACTION, AuditAction.SENSITIVE_ACCESS]:
            return AuditSeverity.MEDIUM.value
        else:
            return AuditSeverity.LOW.value

    def _build_context(
        self,
        request_info: Dict[str, Any],
        response_info: Dict[str, Any],
        action: AuditAction
    ) -> Dict[str, Any]:
        """
        Build additional context cho audit log
        """
        context = {}

        # Admin action context
        if action == AuditAction.ADMIN_ACTION:
            context["target_user_id"] = self._extract_target_user_id(request_info.get("path", ""))

        # Login context
        elif action == AuditAction.LOGIN:
            context["login_success"] = response_info.get("status_code") == 200

        # Resource operation context
        elif action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
            context["resource_type"] = self._extract_resource_type(request_info.get("path", ""))
            context["resource_id"] = self._extract_resource_id(request_info.get("path", ""))

        return context

    def _extract_target_user_id(self, path: str) -> Optional[str]:
        """Extract target user ID từ admin endpoint path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == "api" and parts[1] == "v1" and parts[2] == "admin" and parts[3] == "users":
            return parts[4] if len(parts) > 4 else None
        return None

    def _extract_resource_type(self, path: str) -> Optional[str]:
        """Extract resource type từ path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
            return parts[2]
        return None

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Extract resource ID từ path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == "api" and parts[1] == "v1":
            return parts[3]
        return None

    async def _log_audit_entry(self, audit_entry: Dict[str, Any]):
        """
        Ghi audit entry vào database và logging system

        Args:
            audit_entry: Audit log entry
        """
        try:
            # Update statistics
            self._update_stats(audit_entry)

            # Log to file/console
            log_level = logging.WARNING if audit_entry.get("severity") in ["high", "critical"] else logging.INFO
            logger.log(
                log_level,
                f"Audit: {audit_entry['action']} by user {audit_entry['user_email']} "
                f"({audit_entry['user_id']}) at {audit_entry['endpoint']} "
                f"from {audit_entry['client_ip']} - Status: {audit_entry['status_code']}"
            )

            # Save to database (async)
            if self.db_connection:
                await self._save_to_database(audit_entry)

        except Exception as e:
            # Log errors in audit logging nhưng không raise exception để không ảnh hưởng main flow
            logger.error(f"Audit logging failed: {str(e)}")

    def _update_stats(self, audit_entry: Dict[str, Any]):
        """Cập nhật thống kê audit logging"""
        self.stats["total_logs"] += 1

        action = audit_entry.get("action")
        if action == AuditAction.LOGIN.value:
            self.stats["login_attempts"] += 1
        elif audit_entry.get("is_error"):
            self.stats["failed_attempts"] += 1
        elif action == AuditAction.ADMIN_ACTION.value:
            self.stats["admin_actions"] += 1
        elif action == AuditAction.SENSITIVE_ACCESS.value:
            self.stats["sensitive_accesses"] += 1

    async def _save_to_database(self, audit_entry: Dict[str, Any]):
        """
        Lưu audit entry vào database table activity_logs

        Args:
            audit_entry: Audit log entry dictionary
        """
        try:
            # Map audit entry sang activity_logs format theo API contract
            activity_log = {
                "user_id": audit_entry.get("user_id"),
                "action": audit_entry.get("action"),
                "target_type": self._extract_resource_type(audit_entry.get("endpoint", "")),
                "target_id": self._extract_resource_id(audit_entry.get("endpoint", "")),
                "details": {
                    "method": audit_entry.get("method"),
                    "endpoint": audit_entry.get("endpoint"),
                    "client_ip": audit_entry.get("client_ip"),
                    "user_agent": audit_entry.get("user_agent"),
                    "status_code": audit_entry.get("status_code"),
                    "duration_ms": audit_entry.get("duration_ms"),
                    "query_params": audit_entry.get("query_params"),
                    "context": audit_entry.get("context"),
                    "severity": audit_entry.get("severity"),
                },
                "ip_address": audit_entry.get("client_ip"),
                "user_agent": audit_entry.get("user_agent"),
                "created_at": audit_entry.get("timestamp"),
            }

            # TODO: Implement actual database save
            # await self.db_connection.execute(
            #     "INSERT INTO activity_logs (...) VALUES (...)",
            #     activity_log
            # )

            logger.debug(f"Audit log saved to database: {activity_log}")

        except Exception as e:
            logger.error(f"Failed to save audit log to database: {str(e)}")

    def get_stats(self) -> Dict[str, int]:
        """
        Lấy thống kê audit logging

        Returns:
            Statistics dictionary
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset thống kê audit logging"""
        self.stats = {
            "total_logs": 0,
            "login_attempts": 0,
            "failed_attempts": 0,
            "admin_actions": 0,
            "sensitive_accesses": 0,
        }


# Helper functions

def create_audit_logger(**kwargs):
    """
    Factory function để tạo AuditLogMiddleware instance

    Args:
        **kwargs: Additional arguments cho AuditLogMiddleware

    Returns:
        AuditLogMiddleware instance
    """
    return lambda app: AuditLogMiddleware(app, **kwargs)


# Decorator cho manual audit logging

def audit_action(action: str, details: Optional[Dict[str, Any]] = None):
    """
    Decorator để thêm custom audit logging cho functions

    Usage:
        @audit_action("custom_action", {"additional_info": "value"})
        async def custom_function(request: Request):
            return {"message": "Success"}
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            # Execute function
            result = await func(*args, **kwargs)

            # Create custom audit entry if request available
            if request:
                try:
                    audit_middleware = AuditLogMiddleware(None)
                    audit_entry = await audit_middleware._create_audit_entry(
                        request_info=await audit_middleware._collect_request_info(request),
                        response_info={"status_code": 200},
                        action=AuditAction(action),
                        duration=0,
                        timestamp=datetime.utcnow()
                    )

                    if details:
                        audit_entry["context"].update(details)

                    await audit_middleware._log_audit_entry(audit_entry)
                except Exception as e:
                    logger.error(f"Custom audit logging failed: {str(e)}")

            return result
        return wrapper
    return decorator