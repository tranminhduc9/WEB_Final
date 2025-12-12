"""
Authentication Error Handler.

Global error handler for authentication-related exceptions.
Implementation adapted from task #5 requirements for auth-specific errors.
"""

import logging
from typing import Union

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Safe import with fallback
try:
    from ..auth.jwt_middleware import AuthException
except ImportError:
    # Fallback for standalone usage
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from auth.jwt_middleware import AuthException


logger = logging.getLogger(__name__)


class AuthErrorHandler:
    """
    Authentication Error Handler.

    Handles all authentication-related exceptions and returns consistent error responses.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize Auth Error Handler.

        Args:
            debug: Enable debug mode for detailed error information
        """
        self.debug = debug

    def format_error_response(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        details: Union[list, dict, None] = None,
        field: str = None
    ) -> dict:
        """
        Format consistent error response.

        Args:
            error_code: Machine-readable error code
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
            field: Field name for field-specific errors

        Returns:
            Formatted error response dictionary
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }

        # Add optional fields
        if details is not None:
            response["error"]["details"] = details
        if field:
            response["error"]["field"] = field

        # Add debug information in development
        if self.debug:
            response["debug"] = {
                "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
                "status_code": status_code
            }

        return response

    async def handle_auth_exception(
        self,
        request: Request,
        exc: AuthException
    ) -> JSONResponse:
        """
        Handle custom AuthException.

        Args:
            request: FastAPI request object
            exc: AuthException instance

        Returns:
            JSONResponse with formatted error
        """
        logger.warning(
            f"Auth exception for {request.method} {request.url.path}: "
            f"{exc.detail.get('error', {}).get('code')} - "
            f"{exc.detail.get('error', {}).get('message')}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=self.format_error_response(
                error_code=exc.detail["error"]["code"],
                message=exc.detail["error"]["message"],
                status_code=exc.status_code
            )
        )

    async def handle_http_exception(
        self,
        request: Request,
        exc: HTTPException
    ) -> JSONResponse:
        """
        Handle standard HTTPException.

        Args:
            request: FastAPI request object
            exc: HTTPException instance

        Returns:
            JSONResponse with formatted error
        """
        # Determine error code based on status code
        error_code = {
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR"
        }.get(exc.status_code, "HTTP_ERROR")

        logger.error(
            f"HTTP exception for {request.method} {request.url.path}: "
            f"{exc.status_code} - {str(exc.detail)}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=self.format_error_response(
                error_code=error_code,
                message=str(exc.detail),
                status_code=exc.status_code
            )
        )

    async def handle_validation_error(
        self,
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle RequestValidationError (input validation).

        Args:
            request: FastAPI request object
            exc: RequestValidationError instance

        Returns:
            JSONResponse with formatted validation error
        """
        logger.warning(
            f"Validation error for {request.method} {request.url.path}: "
            f"{len(exc.errors())} validation errors"
        )

        # Format validation errors
        details = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            details.append({
                "field": field,
                "message": error["msg"],
                "value": error.get("input"),
                "type": error["type"]
            })

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=self.format_error_response(
                error_code="VALIDATION_ERROR",
                message="Dữ liệu không hợp lệ",
                status_code=status.HTTP_400_BAD_REQUEST,
                details=details
            )
        )

    async def handle_jwt_errors(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle JWT-specific errors.

        Args:
            request: FastAPI request object
            exc: JWT exception instance

        Returns:
            JSONResponse with formatted JWT error
        """
        import jwt

        if isinstance(exc, jwt.ExpiredSignatureError):
            logger.warning(f"JWT expired for {request.method} {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=self.format_error_response(
                    error_code="TOKEN_EXPIRED",
                    message="Token đã hết hạn",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            )

        elif isinstance(exc, jwt.InvalidTokenError):
            logger.warning(f"Invalid JWT for {request.method} {request.url.path}: {str(exc)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=self.format_error_response(
                    error_code="INVALID_TOKEN",
                    message="Token không hợp lệ",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            )

        # Unknown JWT error
        logger.error(f"Unknown JWT error for {request.method} {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self.format_error_response(
                error_code="INTERNAL_SERVER_ERROR",
                message="Lỗi xác thực server nội bộ",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )

    async def handle_general_error(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Handle unexpected errors.

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse with formatted generic error
        """
        logger.error(
            f"Unexpected error for {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            exc_info=True
        )

        # Don't expose internal error details in production
        error_message = "Lỗi server nội bộ" if not self.debug else str(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self.format_error_response(
                error_code="INTERNAL_SERVER_ERROR",
                message=error_message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        )


# Factory function for creating error handler
def create_auth_error_handler(debug: bool = False) -> AuthErrorHandler:
    """
    Create AuthErrorHandler instance.

    Args:
        debug: Enable debug mode

    Returns:
        AuthErrorHandler instance
    """
    return AuthErrorHandler(debug=debug)


# Global exception handler function
async def auth_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for authentication routes.

    This function can be used as a FastAPI exception handler.
    """
    error_handler = AuthErrorHandler(debug=False)  # Use env variable in real app

    # Route exceptions to appropriate handlers
    if isinstance(exc, AuthException):
        return await error_handler.handle_auth_exception(request, exc)
    elif isinstance(exc, HTTPException):
        return await error_handler.handle_http_exception(request, exc)
    elif isinstance(exc, RequestValidationError):
        return await error_handler.handle_validation_error(request, exc)
    else:
        # Try to handle JWT errors
        try:
            import jwt
            if isinstance(exc, (jwt.ExpiredSignatureError, jwt.InvalidTokenError)):
                return await error_handler.handle_jwt_errors(request, exc)
        except ImportError:
            pass

        # Fall back to general error handler
        return await error_handler.handle_general_error(request, exc)