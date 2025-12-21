"""
Middleware Tests Package

Package chứa tất cả test files cho middleware system.
Tests được tổ chức theo từng module middleware để dễ quản lý và bảo trì.

Test Coverage:
- Authentication middleware (JWT, roles, permissions)
- Rate limiting middleware (memory/Redis, sliding window)
- Email service middleware (SMTP, templates, validation)
- OTP service middleware (generation, validation, encryption)
- File upload middleware (Cloudinary, validation, transformations)
- MongoDB client middleware (CRUD, aggregation, indexes)
- Input validation middleware (schemas, rules, sanitization)
- Error handling middleware (custom errors, logging, responses)
- Response standardization middleware (format consistency)
- Audit logging middleware (action tracking, security events)

Usage:
    pytest tests/middleware/                    # Run all middleware tests
    pytest tests/middleware/test_auth.py     # Run specific middleware tests
    pytest -m "middleware"                    # Run with middleware marker
    pytest -m "unit and middleware"          # Run unit tests only
    pytest -m "integration and middleware"    # Run integration tests only
    pytest -m "slow and middleware"           # Run performance tests

Test Categories:
- unit: Fast unit tests for individual functions/methods
- integration: Tests that verify interaction between components
- middleware: Marker for all middleware-related tests
- slow: Performance and load tests (may take longer)

Environment Setup:
- Tests use mock objects for external dependencies
- Test database/storage use temporary in-memory instances
- Environment variables are overridden for test isolation
"""

__all__ = []