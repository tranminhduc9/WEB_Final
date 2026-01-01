"""
LogSearch Middleware - Ghi lịch sử tìm kiếm vào visit_logs

Middleware chuyên biệt theo API contract để ghi lại hành vi tìm kiếm
của người dùng vào bảng visit_logs cho phân tích và tối ưu.
"""

import time
from datetime import datetime, timedelta
from app.utils.timezone_helper import utc_now
from typing import Dict, Any, Optional, List
from fastapi import Request, Query, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json
import asyncio
from enum import Enum

logger = logging.getLogger(__name__)


class SearchActionType(Enum):
    """Các loại hành động tìm kiếm theo API contract"""
    PLACES_SEARCH = "places_search"
    PLACES_SUGGEST = "places_suggest"
    POSTS_SEARCH = "posts_search"
    USER_SEARCH = "user_search"


class VisitLogEntry:
    """Đối tượng đại diện cho một visit log entry"""

    def __init__(
        self,
        user_id: Optional[str] = None,
        keyword: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        result_count: int = 0,
        response_time: float = 0.0,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        page_url: Optional[str] = None,
        action_type: str = "places_search"
    ):
        """
        Khởi tạo visit log entry

        Args:
            user_id: ID người dùng (nếu đã đăng nhập)
            keyword: Từ khóa tìm kiếm
            filters: Bộ lọc đã áp dụng
            result_count: Số kết quả trả về
            response_time: Thời gian xử lý (ms)
            ip_address: IP address của client
            user_agent: User agent string
            page_url: URL của trang
            action_type: Loại hành động tìm kiếm
        """
        self.id = None  # Sẽ được set khi lưu vào DB
        self.user_id = user_id
        self.keyword = keyword or ""
        self.filters = filters or {}
        self.result_count = result_count
        self.response_time = response_time
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.page_url = page_url
        self.action_type = action_type
        self.visited_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary để lưu vào DB"""
        return {
            "user_id": self.user_id,
            "keyword": self.keyword,
            "filters": json.dumps(self.filters) if self.filters else "{}",
            "result_count": self.result_count,
            "response_time": self.response_time,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "page_url": self.page_url,
            "action_type": self.action_type,
            "visited_at": self.visited_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisitLogEntry":
        """Tạo VisitLogEntry từ dictionary (từ DB)"""
        instance = cls(
            user_id=data.get("user_id"),
            keyword=data.get("keyword"),
            filters=json.loads(data.get("filters", "{}")),
            result_count=data.get("result_count", 0),
            response_time=data.get("response_time", 0.0),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            page_url=data.get("page_url"),
            action_type=data.get("action_type", "places_search")
        )
        instance.id = data.get("id")
        instance.visited_at = data.get("visited_at", utc_now())
        return instance


class LogSearchService:
    """
    Service xử lý logging tìm kiếm theo API contract

    Chuyên trách ghi lại lịch sử tìm kiếm vào visit_logs table.
    """

    def __init__(self, db_session=None):
        """
        Khởi tạo LogSearch service

        Args:
            db_session: Database session instance
        """
        self.db_session = db_session
        self.trending_keywords_cache = {}
        self.last_cache_update = utc_now()

    async def log_search(
        self,
        request: Request,
        action_type: SearchActionType,
        keyword: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        result_count: int = 0,
        response_time: float = 0.0
    ) -> VisitLogEntry:
        """
        Ghi log hành động tìm kiếm vào visit_logs

        Args:
            request: FastAPI request object
            action_type: Loại hành động tìm kiếm
            keyword: Từ khóa tìm kiếm
            filters: Bộ lọc đã áp dụng
            result_count: Số kết quả trả về
            response_time: Thời gian xử lý (ms)

        Returns:
            VisitLogEntry: Entry đã được ghi log
        """
        try:
            # Lấy thông tin từ request
            user_id = self._get_user_id(request)
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "")
            page_url = str(request.url)

            # Tạo log entry
            log_entry = VisitLogEntry(
                user_id=user_id,
                keyword=keyword,
                filters=filters,
                result_count=result_count,
                response_time=response_time,
                ip_address=ip_address,
                user_agent=user_agent,
                page_url=page_url,
                action_type=action_type.value
            )

            # Lưu vào database
            if self.db_session:
                await self._save_to_database(log_entry)
            else:
                await self._save_to_memory(log_entry)

            # Update trending keywords cache
            if keyword:
                self._update_trending_keywords(keyword)

            logger.info(f"Search logged: {action_type.value} - {keyword} by {user_id or 'anonymous'}")
            return log_entry

        except Exception as e:
            logger.error(f"Failed to log search: {str(e)}")
            # Không throw error để không ảnh hưởng đến API response
            return None

    def _get_user_id(self, request: Request) -> Optional[str]:
        """Lấy user ID từ request state (đã được set bởi Auth middleware)"""
        if hasattr(request.state, 'user') and request.state.user:
            return str(request.state.user.get('user_id'))
        return None

    def _get_client_ip(self, request: Request) -> str:
        """Lấy client IP address từ các headers"""
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
                return ip.strip()

        return request.client.host if request.client else "unknown"

    def _update_trending_keywords(self, keyword: str):
        """Cập nhật trending keywords cache"""
        keyword_lower = keyword.lower().strip()
        if keyword_lower in self.trending_keywords_cache:
            self.trending_keywords_cache[keyword_lower] += 1
        else:
            self.trending_keywords_cache[keyword_lower] = 1

    async def _save_to_database(self, log_entry: VisitLogEntry):
        """
        Lưu log entry vào database visit_logs table

        Args:
            log_entry: VisitLogEntry cần lưu
        """
        try:
            # TODO: Implement actual database save
            # Ví dụ với SQLAlchemy:
            # from database.models import VisitLog
            # db_log = VisitLog(**log_entry.to_dict())
            # self.db_session.add(db_log)
            # await self.db_session.commit()
            # log_entry.id = db_log.id

            # Mock implementation
            pass

        except Exception as e:
            logger.error(f"Failed to save search log to database: {str(e)}")
            raise

    async def _save_to_memory(self, log_entry: VisitLogEntry):
        """
        Fallback: lưu vào memory khi không có database

        Args:
            log_entry: VisitLogEntry cần lưu
        """
        if not hasattr(self, '_memory_storage'):
            self._memory_storage = []

        # Assign mock ID
        log_entry.id = len(self._memory_storage) + 1
        self._memory_storage.append(log_entry)

        # Keep only last 1000 entries in memory
        if len(self._memory_storage) > 1000:
            self._memory_storage = self._memory_storage[-1000:]

    async def get_trending_keywords(
        self,
        limit: int = 10,
        time_range: str = "7days"
    ) -> List[Dict[str, Any]]:
        """
        Lấy trending keywords theo thời gian

        Args:
            limit: Số keywords trả về
            time_range: Khoảng thời gian (1day, 7days, 30days)

        Returns:
            List[Dict]: Danh sách trending keywords với count
        """
        # Trong thực tế, query từ database:
        # SELECT keyword, COUNT(*) as count
        # FROM visit_logs
        # WHERE visited_at >= NOW() - INTERVAL
        # GROUP BY keyword
        # ORDER BY count DESC
        # LIMIT ?

        # Mock implementation using cache
        sorted_keywords = sorted(
            self.trending_keywords_cache.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"keyword": kw, "count": count}
            for kw, count in sorted_keywords[:limit]
        ]

    async def get_user_search_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[VisitLogEntry]:
        """
        Lấy lịch sử tìm kiếm của user

        Args:
            user_id: ID của user
            limit: Số logs tối đa

        Returns:
            List[VisitLogEntry]: Lịch sử tìm kiếm
        """
        # Trong thực tế, query từ database:
        # SELECT * FROM visit_logs
        # WHERE user_id = ?
        # ORDER BY visited_at DESC
        # LIMIT ?

        # Mock implementation
        if hasattr(self, '_memory_storage'):
            user_logs = [
                log for log in self._memory_storage
                if log.user_id == user_id
            ]
            return sorted(user_logs, key=lambda x: x.visited_at, reverse=True)[:limit]

        return []


class LogSearchMiddleware(BaseHTTPMiddleware):
    """
    Middleware tự động log search requests theo API contract

    Tự động áp dụng LogSearch cho các endpoint tìm kiếm:
    - GET /api/v1/places/suggest
    - GET /api/v1/places
    - GET /api/v1/posts
    """

    def __init__(self, app, db_session=None):
        """
        Khởi tạo middleware

        Args:
            app: FastAPI application
            db_session: Database session
        """
        super().__init__(app)
        self.log_search_service = LogSearchService(db_session)

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và log nếu là search endpoint

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response với search logging đã được áp dụng
        """
        start_time = time.time()

        # Check if this is a search request
        search_info = self._identify_search_request(request)
        if search_info:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            # Extract result count from response
            result_count = self._extract_result_count(response)

            # Extract search parameters
            keyword = self._extract_keyword(request, search_info)
            filters = self._extract_filters(request, search_info)

            # Log the search
            await self.log_search_service.log_search(
                request=request,
                action_type=search_info["action_type"],
                keyword=keyword,
                filters=filters,
                result_count=result_count,
                response_time=response_time
            )

            return response

        # Non-search request, process normally
        return await call_next(request)

    def _identify_search_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Nhận diện loại search request

        Args:
            request: FastAPI request

        Returns:
            Dict: Thông tin search hoặc None
        """
        path = request.url.path
        method = request.method

        # Places suggest endpoint
        if path == "/api/v1/places/suggest" and method == "GET":
            return {"action_type": SearchActionType.PLACES_SUGGEST, "keyword_param": "keyword"}

        # Places search endpoint
        if path == "/api/v1/places" and method == "GET":
            return {"action_type": SearchActionType.PLACES_SEARCH, "keyword_param": "keyword"}

        # Posts search endpoint
        if path == "/api/v1/posts" and method == "GET":
            return {"action_type": SearchActionType.POSTS_SEARCH, "keyword_param": "keyword"}

        # User search endpoint (if exists)
        if path.startswith("/api/v1/users/search") and method == "GET":
            return {"action_type": SearchActionType.USER_SEARCH, "keyword_param": "q"}

        return None

    def _extract_keyword(self, request: Request, search_info: Dict[str, Any]) -> Optional[str]:
        """Trích xuất keyword từ request parameters"""
        keyword_param = search_info["keyword_param"]
        return request.query_params.get(keyword_param, "").strip() or None

    def _extract_filters(self, request: Request, search_info: Dict[str, Any]) -> Dict[str, Any]:
        """Trích xuất filters từ request parameters"""
        filters = {}

        # Common filter fields theo API contract
        filter_fields = [
            "district_id", "category_id", "price_min", "price_max",
            "rating", "tag", "sort", "date_range", "page", "limit"
        ]

        for field in filter_fields:
            if field in request.query_params:
                value = request.query_params[field]
                # Try to convert numeric values
                if field in ["district_id", "category_id", "price_min", "price_max", "rating", "page", "limit"]:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                filters[field] = value

        return filters

    def _extract_result_count(self, response) -> int:
        """
        Trích xuất số kết quả từ API response

        Args:
            response: FastAPI response

        Returns:
            int: Số kết quả
        """
        try:
            # Try to get result count from response body
            if hasattr(response, 'body'):
                body = json.loads(response.body.decode())

                # Check for pagination info
                if "pagination" in body and "total_items" in body["pagination"]:
                    return body["pagination"]["total_items"]

                # Check for data array
                if "data" in body and isinstance(body["data"], list):
                    return len(body["data"])

                # Check for direct array response
                if isinstance(body, list):
                    return len(body)

        except Exception as e:
            logger.warning(f"Failed to extract result count: {str(e)}")

        return 0


# Global instances
log_search_service = LogSearchService()


# Decorator cho manual search logging
def log_search_action(action_type: SearchActionType, keyword_param: str = "keyword"):
    """
    Decorator để log search action manually

    Args:
        action_type: Loại hành động tìm kiếm
        keyword_param: Tên parameter chứa keyword
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request from kwargs if available
            request = kwargs.get('request')
            if not request:
                return await func(*args, **kwargs)

            start_time = time.time()
            result = await func(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000

            # Extract keyword
            keyword = kwargs.get(keyword_param) or request.query_params.get(keyword_param)

            # Extract filters from query params
            filters = {}
            for param, value in request.query_params.items():
                if param != keyword_param:
                    filters[param] = value

            # Extract result count
            result_count = 0
            if isinstance(result, list):
                result_count = len(result)
            elif hasattr(result, '__len__'):
                result_count = len(result)

            # Log the search
            await log_search_service.log_search(
                request=request,
                action_type=action_type,
                keyword=keyword,
                filters=filters,
                result_count=result_count,
                response_time=response_time
            )

            return result
        return wrapper
    return decorator


# Utility functions
async def get_popular_searches(time_range: str = "7days", limit: int = 10) -> List[Dict[str, Any]]:
    """
    Lấy các tìm kiếm phổ biến

    Args:
        time_range: Khoảng thời gian (1day, 7days, 30days)
        limit: Số kết quả tối đa

    Returns:
        List[Dict]: Danh sách trending searches
    """
    return await log_search_service.get_trending_keywords(limit, time_range)


async def get_user_search_activity(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Lấy hoạt động tìm kiếm của user trong N ngày qua

    Args:
        user_id: ID của user
        days: Số ngày cần query

    Returns:
        List[Dict]: Lịch sử tìm kiếm
    """
    logs = await log_search_service.get_user_search_history(user_id, limit=100)

    # Filter by date range
    cutoff_date = utc_now() - timedelta(days=days)
    recent_logs = [
        log for log in logs
        if log.visited_at >= cutoff_date
    ]

    return [
        {
            "keyword": log.keyword,
            "action_type": log.action_type,
            "result_count": log.result_count,
            "visited_at": log.visited_at.isoformat(),
            "filters": log.filters
        }
        for log in recent_logs
    ]