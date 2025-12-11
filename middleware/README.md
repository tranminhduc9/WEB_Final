# WEB Final Middleware

Middleware cho WEB Final API với xác thực JWT, phân quyền, giới hạn truy cập và xử lý lỗi.

## 🚀 Cài Đặt

```bash
pip install fastapi pydantic redis PyJWT
```

## 📖 Sử Dụng

```python
from fastapi import FastAPI
from middleware.auth.jwt_middleware import JWTAuthMiddleware
from middleware.security.rate_limiter import RateLimiterMiddleware
from middleware.validation.validator import ValidationMiddleware
from middleware.error.global_error_handler import ErrorHandlerMiddleware

app = FastAPI()

# Thêm middleware (thứ tự quan trọng)
app.add_middleware(ErrorHandlerMiddleware)    # Trong cùng
app.add_middleware(ValidationMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(JWTAuthMiddleware, excluded_paths=["/login", "/register"])
```

## ✅ Tính Năng

- **🔐 Xác thực JWT** - Token validation với blacklist
- **👥 Phân quyền** - Role-based (User/Mod/Admin)
- **⚡ Giới hạn truy cập** - 3 cấp: CAO(5)/TRUNG BÌNH(20)/THẤP(100) req/phút
- **✅ Kiểm tra dữ liệu** - Pydantic schemas
- **🚨 Xử lý lỗi** - Centralized error handling
- **📝 Audit Log** - Activity tracking

## 🧪 Testing

```bash
# Chạy tất cả tests
python run_tests.py

# Chạy với pytest
python -m pytest tests/ -v
```

**Kết quả**: 23/23 tests passing ✅

## 📁 Cấu Trúc

```
middleware/
├── auth/          # Xác thực & Phân quyền
├── security/      # Giới hạn truy cập
├── validation/    # Kiểm tra dữ liệu
├── audit/        # Audit logging
├── error/        # Xử lý lỗi
├── config/       # Cấu hình
└── tests/        # Test suite
```

## 🔧 Cấu Hình

```bash
# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# Redis
REDIS_URL=redis://localhost:6379/0

# App
DEBUG=false
LOG_LEVEL=INFO
```

## 📚 Tài Liệu

- [Hướng dẫn chi tiết](MIDDLEWARE_GUIDE.md)
- [Tests](tests/README.md)
- [Nhật ký phát triển](DEVELOPMENT_LOG.md)

---

**Phiên bản**: 2.0 | **Trạng thái**: Production Ready ✅