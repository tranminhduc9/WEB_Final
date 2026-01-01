"""
Search Logging Middleware

Module này ghi lại lịch sử tìm kiếm của người dùng
vào bảng visit_logs cho phân tích và tối ưu.
"""

import time
from datetime import datetime
from app.utils.timezone_helper import utc_now
from typing import Dict, Any, Optional
from fastapi import Request, Query
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json

logger = logging.getLogger(__name__)


class SearchLogger:
    """
    Class ghi log hành vi tìm kiếm người dùng
    """

    def __init__(self):
        """Khởi tạo search logger"""
        self.search_keywords = {}  # Cache cho trending keywords

    async def log_search(
        self,
        request: Request,
        keyword: str,
        filters: Dict[str, Any] = None,
        result_count: int = 0,
        response_time: float = 0.0
    ):
        """
        Ghi log hành động tìm kiếm

        Args:
            request: FastAPI request
            keyword: Từ khóa tìm kiếm
            filters: Bộ lọc áp dụng
            result_count: Số kết quả trả về
            response_time: Thời gian xử lý
        """
        try:
            # Lấy thông tin user
            user_id = self._get_user_id(request)
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "")

            # Tạo log entry
            log_data = {
                "user_id": user_id,
                "keyword": keyword,
                "filters": filters or {},
                "result_count": result_count,
                "response_time": response_time,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "page_url": str(request.url),
                "visited_at": utc_now()
            }

            # Log vào database (implement sau)
            await self._save_to_database(log_data)

            # Update trending keywords cache
            self._update_trending_keywords(keyword)

            logger.info(f"Search logged: {keyword} by {user_id or 'anonymous'}")

        except Exception as e:
            logger.error(f"Failed to log search: {str(e)}")

    def _get_user_id(self, request: Request) -> Optional[int]:
        """Lấy user ID từ request"""
        if hasattr(request.state, 'user') and request.state.user:
            return request.state.user.get('user_id')
        return None

    def _get_client_ip(self, request: Request) -> str:
        """Lấy client IP"""
        headers = ["X-Forwarded-For", "X-Real-IP", "X-Client-IP"]
        for header in headers:
            ip = request.headers.get(header)
            if ip:
                return ip.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _update_trending_keywords(self, keyword: str):
        """Cập nhật trending keywords cache"""
        if keyword in self.search_keywords:
            self.search_keywords[keyword] += 1
        else:
            self.search_keywords[keyword] = 1

    async def _save_to_database(self, log_data: Dict[str, Any]):
        """
        Lưu log vào database visit_logs

        Args:
            log_data: Dữ liệu log cần lưu
        """
        try:
            from config.database import SessionLocal, VisitLog
            import re
            
            db = SessionLocal()
            try:
                # Extract place_id from URL if visiting a place detail page
                place_id = None
                page_url = log_data.get("page_url", "")
                place_match = re.search(r'/api/v1/places/(\d+)', page_url)
                if place_match:
                    place_id = int(place_match.group(1))
                
                # Extract post_id from URL if visiting a post detail page
                post_id = None
                post_match = re.search(r'/api/v1/posts/([a-f0-9]+)', page_url)
                if post_match:
                    post_id = post_match.group(1)
                
                # Tạo VisitLog record
                visit_log = VisitLog(
                    user_id=log_data.get("user_id"),
                    place_id=place_id,
                    post_id=post_id,
                    page_url=page_url,
                    ip_address=log_data.get("ip_address"),
                    user_agent=log_data.get("user_agent"),
                    visited_at=log_data.get("visited_at")
                )
                
                db.add(visit_log)
                db.commit()
                logger.debug(f"Visit log saved to database: {page_url}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to save visit log to database: {e}")
            finally:
                db.close()
                
        except ImportError as e:
            logger.warning(f"Database not available for visit logging: {e}")

    def get_trending_keywords(self, limit: int = 10) -> list:
        """
        Lấy danh sách trending keywords

        Args:
            limit: Số keywords trả về

        Returns:
            list: Danh sách trending keywords
        """
        # Sort by count and return top keywords
        sorted_keywords = sorted(
            self.search_keywords.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [{"keyword": kw, "count": count} for kw, count in sorted_keywords[:limit]]


class SearchLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware tự động log search requests
    """

    def __init__(self, app):
        super().__init__(app)
        self.search_logger = SearchLogger()

    async def dispatch(self, request: Request, call_next):
        """
        Xử lý request và log nếu là search endpoint

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response: Response với search logging
        """
        start_time = time.time()

        # Check if this is a search request
        if self._is_search_request(request):
            # Extract search parameters
            search_params = self._extract_search_params(request)

            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000

            # Extract result count from response if possible
            result_count = self._extract_result_count(response)

            # Log the search
            await self.search_logger.log_search(
                request=request,
                keyword=search_params.get("keyword", ""),
                filters=search_params.get("filters", {}),
                result_count=result_count,
                response_time=response_time
            )

            return response

        # Non-search request, just process normally
        return await call_next(request)

    def _is_search_request(self, request: Request) -> bool:
        """
        Kiểm tra có phải search request không

        Args:
            request: FastAPI request

        Returns:
            bool: True nếu là search request
        """
        search_paths = [
            "/api/v1/places",
            "/api/v1/posts",
            "/api/v1/users/search"
        ]

        return any(request.url.path.startswith(path) for path in search_paths)

    def _extract_search_params(self, request: Request) -> Dict[str, Any]:
        """
        Trích xuất search parameters từ request

        Args:
            request: FastAPI request

        Returns:
            Dict: Search parameters
        """
        params = dict(request.query_params)

        search_params = {
            "keyword": params.get("keyword", ""),
            "filters": {}
        }

        # Extract common filters
        filter_fields = [
            "district_id", "category_id", "price_min", "price_max",
            "rating", "tag", "sort", "date_range"
        ]

        for field in filter_fields:
            if field in params:
                search_params["filters"][field] = params[field]

        return search_params

    def _extract_result_count(self, response) -> int:
        """
        Trích xuất số kết quả từ response

        Args:
            response: FastAPI response

        Returns:
            int: Số kết quả
        """
        try:
            # Try to get result count from response body
            if hasattr(response, 'body'):
                import json
                body = json.loads(response.body.decode())
                if isinstance(body.get("data"), list):
                    return len(body["data"])
                elif body.get("pagination", {}).get("total_items"):
                    return body["pagination"]["total_items"]
        except Exception:
            pass

        return 0


# Global search logger instance
search_logger = SearchLogger()


# Decorator cho manual search logging
def log_search(keyword_param: str = "keyword", filters_param: str = None):
    """
    Decorator để log search manually

    Args:
        keyword_param: Tên parameter chứa keyword
        filters_param: Tên parameter chứa filters
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract keyword
            keyword = kwargs.get(keyword_param, "")

            # Extract filters
            filters = {}
            if filters_param and filters_param in kwargs:
                filters = kwargs[filters_param]

            # Get request from kwargs if available
            request = kwargs.get('request')

            # Process function
            start_time = time.time()
            result = await func(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000

            # Log search if request available
            if request:
                result_count = 0
                if isinstance(result, list):
                    result_count = len(result)
                elif hasattr(result, '__len__'):
                    result_count = len(result)

                await search_logger.log_search(
                    request=request,
                    keyword=keyword,
                    filters=filters,
                    result_count=result_count,
                    response_time=response_time
                )

            return result
        return wrapper
    return decorator


# Utility functions
def get_search_suggestions(keyword: str, limit: int = 5) -> list:
    """
    Lấy gợi ý tìm kiếm dựa trên keyword

    Args:
        keyword: Từ khóa hiện tại
        limit: Số gợi ý tối đa

    Returns:
        list: Danh sách gợi ý
    """
    # TODO: Implement search suggestions
    # Có thể dùng Elasticsearch hoặc simple text matching
    return []


def get_popular_searches(time_range: str = "7days", limit: int = 10) -> list:
    """
    Lấy các tìm kiếm phổ biến

    Args:
        time_range: Khoảng thời gian (1day, 7days, 30days)
        limit: Số kết quả tối đa

    Returns:
        list: Danh sách tìm kiếm phổ biến
    """
    # TODO: Implement popular searches from database
    return search_logger.get_trending_keywords(limit)