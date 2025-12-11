"""
404 Not Found Handler Middleware.

This middleware catches all requests to non-existent routes.
Implementation following Task #6 requirements - 404 Not Found handler.
"""
import datetime
import logging
from typing import List, Optional

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse


logger = logging.getLogger(__name__)


class NotFoundMiddleware(BaseHTTPMiddleware):
    """
    404 Not Found Handler Middleware.

    Catches all requests to non-existent routes and returns proper 404 responses.
    Must be placed after all route definitions.
    """

    def __init__(
        self,
        app,
        skip_paths: Optional[List[str]] = None,
        include_route_info: bool = True,
        log_404s: bool = True,
        custom_message: Optional[str] = None
    ):
        """
        Initialize 404 Not Found Handler.

        Args:
            app: FastAPI application instance
            skip_paths: Paths to skip 404 handling
            include_route_info: Include route information in response
            log_404s: Enable 404 logging
            custom_message: Custom 404 message
        """
        super().__init__(app)

        self.skip_paths = skip_paths or [
            "/favicon.ico",
            "/robots.txt",
            "/sitemap.xml",
            "/health",  # In case health check fails
        ]
        self.include_route_info = include_route_info
        self.log_404s = log_404s
        self.custom_message = custom_message

        # Track registered routes to identify 404s
        self.registered_routes = set()

    async def dispatch(self, request: Request, call_next):
        """
        Process request and handle 404 responses.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response or 404 response for non-existent routes
        """
        try:
            response = await call_next(request)

            # Check if this is a 404 response from upstream
            if response.status_code == status.HTTP_404_NOT_FOUND:
                return await self._create_404_response(request)

            return response

        except HTTPException as exc:
            # Check if this is a 404 exception
            if exc.status_code == status.HTTP_404_NOT_FOUND:
                return await self._create_404_response(request)

            # Re-raise other HTTP exceptions
            raise

        except Exception as e:
            # Log unexpected errors but don't convert them to 404
            logger.error(f"Unexpected error in 404 middleware: {str(e)}")
            raise

    async def _create_404_response(self, request: Request) -> Response:
        """
        Create a 404 response.

        Args:
            request: FastAPI request object

        Returns:
            JSONResponse with 404 status and error details
        """
        # Log 404 request if enabled
        if self.log_404s:
            logger.warning(
                f"404 - Route not found: {request.method} {request.url.path} "
                f"(User-Agent: {request.headers.get('user-agent', 'Unknown')})"
            )

        # Determine error message
        if self.custom_message:
            message = self.custom_message
        else:
            message = f"Route {request.method} {request.url.path} không tồn tại"

        # Create error response
        error_response = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": message,
                "timestamp": self._get_timestamp()
            }
        }

        # Add route information if enabled
        if self.include_route_info:
            error_response["error"]["route_info"] = {
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": {
                    "content_type": request.headers.get("content-type"),
                    "accept": request.headers.get("accept"),
                    "user_agent": request.headers.get("user-agent")
                }
            }

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.

        Returns:
            ISO formatted timestamp string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def register_route(self, path: str, method: str = "GET"):
        """
        Register a route to prevent false 404s.

        Args:
            path: Route path
            method: HTTP method
        """
        route_key = f"{method}:{path}"
        self.registered_routes.add(route_key)

    def is_route_registered(self, path: str, method: str = "GET") -> bool:
        """
        Check if a route is registered.

        Args:
            path: Route path
            method: HTTP method

        Returns:
            True if route is registered
        """
        route_key = f"{method}:{path}"
        return route_key in self.registered_routes


# Alternative approach: 404 handler as a route
def create_404_handler(custom_message: Optional[str] = None, include_route_info: bool = True):
    """
    Create a 404 handler function.

    Usage:
        app.add_exception_handler(404, create_404_handler())

    Args:
        custom_message: Custom 404 message
        include_route_info: Include route information in response

    Returns:
        404 handler function
    """

    async def not_found_handler(request: Request, exc: HTTPException):
        """Handle 404 errors."""

        if exc.status_code != status.HTTP_404_NOT_FOUND:
            raise exc

        # Log 404 request
        logger.warning(
            f"404 - Route not found: {request.method} {request.url.path}"
        )

        # Determine error message
        if custom_message:
            message = custom_message
        else:
            message = f"Route {request.method} {request.url.path} không tồn tại"

        # Create error response
        error_response = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        # Add route information if enabled
        if include_route_info:
            error_response["error"]["route_info"] = {
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params)
            }

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )

    return not_found_handler


# Simple 404 response factory
def create_simple_404_response(
    method: str,
    path: str,
    custom_message: Optional[str] = None
) -> dict:
    """
    Create a simple 404 response.

    Args:
        method: HTTP method
        path: Request path
        custom_message: Custom error message

    Returns:
        Formatted 404 response dictionary
    """
    if custom_message:
        message = custom_message
    else:
        message = f"Route {method} {path} không tồn tại"

    return {
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": message
        }
    }


# Middleware factory function
def create_not_found_middleware(**kwargs):
    """
    Factory function to create NotFoundMiddleware instances.

    Args:
        **kwargs: Additional keyword arguments for NotFoundMiddleware

    Returns:
        NotFoundMiddleware instance
    """
    return lambda app: NotFoundMiddleware(app, **kwargs)


# Usage examples:
#
# # Option 1: Using middleware (recommended for FastAPI)
# app.add_middleware(
#     NotFoundMiddleware,
#     skip_paths=["/favicon.ico", "/robots.txt"],
#     include_route_info=True
# )
#
# # Option 2: Using exception handler
# from fastapi import HTTPException
# app.add_exception_handler(404, create_404_handler(
#     custom_message="Endpoint không tìm thấy",
#     include_route_info=True
# ))
#
# # Option 3: Manual 404 response
# from starlette.requests import Request
# from starlette.responses import JSONResponse
# from fastapi import status
#
# async def manual_404_handler(request: Request):
#     response_data = create_simple_404_response(
#         request.method,
#         request.url.path,
#         "API endpoint không tồn tại"
#     )
#     return JSONResponse(
#         status_code=status.HTTP_404_NOT_FOUND,
#         content=response_data
#     )
#
# # Register route for 404s (must be last)
# app.add_route("/{path:path}", manual_404_handler, methods=["GET", "POST", "PUT", "DELETE"])