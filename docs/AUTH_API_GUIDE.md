# Hướng dẫn Chạy và Test Authentication API

## 📋 Tổng quan

Đã implement hoàn chỉnh hệ thống Authentication với các tính năng:
- ✅ Đăng ký user với email validation (Hunter.io)
- ✅ Đăng nhập với JWT tokens
- ✅ Refresh token mechanism
- ✅ Logout
- ✅ Get user profile
- ✅ Password hashing với bcrypt
- ✅ Tuân thủ OpenAPI specification

---

## 🚀 Bước 1: Chuẩn bị môi trường

### 1.1. Cài đặt Python dependencies

```bash
# Điều hướng đến thư mục gốc
cd C:\Users\hvphu\Desktop\WEB_Final

# Cài đặt dependencies
pip install -r requirements.txt
```

### 1.2. Kiểm tra PostgreSQL database

Đảm bảo PostgreSQL đang chạy và có database `hanoi_travel`:

```bash
# Test connection
psql -U postgres -d hanoi_travel -c "SELECT 1;"
```

Hoặc sử dụng Docker (nếu chưa có database):

```bash
cd src
docker-compose up -d
```

### 1.3. Kiểm tra file .env

File `.env` ở project root đã có đầy đủ config quan trọng:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/hanoi_travel

# JWT
JWT_SECRET_KEY=hanoi-travel-super-secret-key-change-in-production-2024

# Hunter.io (đã có API key)
HUNTER_IO_API_KEY=6985d13bbd5def38e23747042722611b8100c927

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=true
```

---

## 🏃 Bước 2: Chạy Server

### Cách 1: Chạy trực tiếp với Python

```bash
# Windows PowerShell
cd C:\Users\hvphu\Desktop\WEB_Final
python -m src.backend.app.main

# Hoặc dùng uvicorn trực tiếp
uvicorn src.backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Cách 2: Chạy với VS Code debugger

1. Mở VS Code
2. Mở file `src/backend/app/main.py`
3. Nhấn F5 hoặc chọn Run → Start Debugging

### Kiểm tra server đang chạy:

Truy cập:
- Server info: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 🧪 Bước 3: Test API Endpoints

### 3.1. Test Đăng Ký User (POST /api/v1/auth/register)

Sử dụng PowerShell:

```powershell
# Test đăng ký với email hợp lệ
$body = @{
    full_name = "Nguyen Van A"
    email = "test@example.com"
    password = "Password@123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Response thành công (201):**
```json
{
  "success": true,
  "message": "Đăng ký thành công",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "full_name": "Nguyen Van A",
      "email": "test@example.com",
      "avatar_url": null,
      "role_id": 3
    }
  }
}
```

**Response lỗi (400) - Email không hợp lệ:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email is not deliverable"
  }
}
```

### 3.2. Test Đăng Nhập (POST /api/v1/auth/login)

```powershell
$body = @{
    email = "test@example.com"
    password = "Password@123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

# Lưu access token
$token = $response.data.access_token
Write-Host "Access Token: $token"
```

**Response thành công (200):**
```json
{
  "success": true,
  "message": "Đăng nhập thành công",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "full_name": "Nguyen Van A",
      "avatar_url": null,
      "role_id": 3
    }
  }
}
```

### 3.3. Test Refresh Token (POST /api/v1/auth/refresh)

```powershell
# Sử dụng refresh_token từ login response
$body = @{
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/refresh" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Response thành công (200):**
```json
{
  "success": true,
  "message": "Refresh token thành công",
  "data": {
    "access_token": "new_access_token...",
    "refresh_token": "new_refresh_token..."
  }
}
```

### 3.4. Test Get Profile (GET /api/v1/users/me)

```powershell
# Sử dụng access_token từ login/refresh response
$headers = @{
    Authorization = "Bearer YOUR_ACCESS_TOKEN_HERE"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/users/me" `
    -Method GET `
    -Headers $headers
```

**Response thành công (200):**
```json
{
  "success": true,
  "message": "Thành công",
  "data": {
    "user": {
      "id": 1,
      "full_name": "Nguyen Van A",
      "email": "test@example.com",
      "phone": null,
      "avatar": null,
      "bio": null,
      "role": "user",
      "is_active": true,
      "is_verified": false,
      "reputation_score": 0.0,
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00",
      "last_login": "2025-01-15T10:35:00"
    },
    "stats": {
      "posts_count": 0
    },
    "recent_favorites": [],
    "recent_posts": []
  }
}
```

### 3.5. Test Logout (POST /api/v1/auth/logout)

```powershell
$headers = @{
    Authorization = "Bearer YOUR_ACCESS_TOKEN_HERE"
}

$body = @{
    refresh_token = "YOUR_REFRESH_TOKEN_HERE"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/logout" `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -ContentType "application/json"
```

**Response thành công (200):**
```json
{
  "success": true,
  "message": "Đăng xuất thành công",
  "data": {}
}
```

---

## 🧪 Test với Postman

### Import Collection

Để dễ dàng test, bạn có thể import Postman Collection:

1. Mở Postman
2. Tạo mới collection với name "Hanoi Travel Auth"
3. Thêm các requests sau:

#### Request 1: Register
- Method: POST
- URL: `http://127.0.0.1:8000/api/v1/auth/register`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
    "full_name": "Test User",
    "email": "testuser@gmail.com",
    "password": "TestPass@123"
}
```

#### Request 2: Login
- Method: POST
- URL: `http://127.0.0.1:8000/api/v1/auth/login`
- Headers: `Content-Type: application/json`
- Body:
```json
{
    "email": "testuser@gmail.com",
    "password": "TestPass@123"
}
```

#### Request 3: Get Profile
- Method: GET
- URL: `http://127.0.0.1:8000/api/v1/users/me`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer {{access_token}}`

---

## 🔍 Xử lý lỗi phổ biến

### Lỗi 1: "Database connection failed"

**Nguyên nhân:** PostgreSQL chưa chạy hoặc sai config

**Giải pháp:**
```bash
# Kiểm tra PostgreSQL service
# Windows:
Get-Service -Name postgresql*

# Start service nếu chưa chạy
Start-Service postgresql-x64-14  # Thay version của bạn
```

### Lỗi 2: "Hunter.io validation failed"

**Nguyên nhân:** API key không hợp lệ hoặc hết quota

**Giải pháp:**
- Kiểm tra `HUNTER_IO_API_KEY` trong .env
- Free tier: 50 requests/month
- Nếu hết quota, code sẽ tự động skip validation và tiếp tục

### Lỗi 3: "Module not found"

**Nguyên nhân:** Chưa cài đặt đủ dependencies

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### Lỗi 4: Password validation error

**Nguyên nhân:** Password không đủ mạnh

**Yêu cầu password:**
- Ít nhất 8 ký tự
- Chứa chữ hoa (A-Z)
- Chứa chữ thường (a-z)
- Chứa số (0-9)
- Chứa ký tự đặc biệt (!@#$%^&*...)

**Ví dụ password hợp lệ:** `Password@123`

---

## 📊 Kiểm tra Database

Sau khi test, bạn có thể kiểm tra data trong database:

```sql
-- Kết nối vào database
psql -U postgres -d hanoi_travel

-- Xem danh sách users
SELECT id, full_name, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;

-- Xem chi tiết user
SELECT * FROM users WHERE email = 'test@example.com';
```

---

## ✅ Checklist

- [x] Tạo User model trong database.py
- [x] Implement Hunter.io email validator
- [x] Implement AuthService với register, login, refresh, logout
- [x] Tạo API routes cho auth endpoints
- [x] Cấu hình FastAPI app với CORS
- [x] Tạo health check endpoints
- [x] Tuân thủ OpenAPI specification
- [x] Comment code bằng tiếng Việt
- [x] Xử lý errors với appropriate status codes

---

## 📚 Cấu trúc Code

```
src/backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   └── v1/
│   │       └── auth.py            # Auth endpoints (register, login, refresh, logout)
│   └── services/
│       └── auth_service.py        # Business logic cho authentication
├── config/
│   └── database.py                # Database config & User model
├── middleware/
│   ├── auth.py                    # JWT authentication middleware
│   ├── validator.py               # Input validation
│   └── response.py                # Response standardization
└── utils/
    └── email_validator.py         # Hunter.io email validator
```

---

## 🎯 Tiếp theo

Sau khi Authentication đã hoạt động, bạn có thể implement:
1. User profile management
2. Places API
3. Posts & Comments API
4. Chatbot integration
5. Admin endpoints

Cần hỗ trợ thêm cứ hỏi nhé! 🚀
