# BACKEND API DOCUMENTATION

**Version:** 1.0.0 | **Updated:** 2026-01-03 | **Author:** Hoang Van Phu

---

## 1. Tổng quan

Hanoivivu API là RESTful backend service sử dụng FastAPI framework, phục vụ nền tảng du lịch Hà Nội.

### Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI >= 0.104.0 |
| Server | Uvicorn >= 0.24.0 |
| Auth | JWT (PyJWT), bcrypt |
| AI | Google Gemini |
| Email | SendGrid |
| Storage | Local / AWS S3 |

---

## 2. Cấu trúc dự án

```
src/backend/
├── run.py                    # Entry point
├── requirements.txt
├── app/
│   ├── main.py               # FastAPI instance
│   ├── api/v1/               # API routes
│   │   ├── auth.py           # Authentication
│   │   ├── users.py          # User management
│   │   ├── places.py         # Places CRUD
│   │   ├── posts.py          # Posts/Reviews
│   │   ├── admin.py          # Admin panel
│   │   ├── chatbot.py        # AI chatbot
│   │   ├── upload.py         # File upload
│   │   └── logs.py           # System logs
│   ├── chatbot/              # Gemini AI integration
│   ├── services/             # Business logic
│   └── utils/                # Helper functions
├── config/                   # Configuration
└── middleware/               # Middleware components
```

---

## 3. API Endpoints

### 3.1 Authentication `/api/v1/auth`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Đăng ký tài khoản | No |
| POST | `/login` | Đăng nhập | No |
| POST | `/refresh` | Refresh token | No |
| POST | `/logout` | Đăng xuất | Optional |
| GET | `/me` | Thông tin user hiện tại | Yes |

### 3.2 Users `/api/v1/users`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/me` | Get profile | Yes |
| PUT | `/me` | Update profile | Yes |
| PUT | `/change-password` | Đổi mật khẩu | Yes |
| POST | `/avatar` | Upload avatar | Yes |
| DELETE | `/avatar` | Xóa avatar | Yes |
| GET | `/{user_id}` | Public profile | No |

### 3.3 Places `/api/v1/places`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Danh sách địa điểm | No |
| GET | `/search` | Tìm kiếm | No |
| GET | `/suggestions` | Gợi ý tìm kiếm | No |
| GET | `/nearby` | Địa điểm lân cận | No |
| GET | `/districts` | Danh sách quận | No |
| GET | `/types` | Loại địa điểm | No |
| GET | `/{place_id}` | Chi tiết | Optional |
| POST | `/{place_id}/favorite` | Toggle yêu thích | Yes |

### 3.4 Posts `/api/v1/posts`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Feed bài viết | Optional |
| POST | `/` | Tạo bài viết | Yes |
| GET | `/{post_id}` | Chi tiết bài viết | Optional |
| DELETE | `/{post_id}` | Xóa bài viết | Yes |
| POST | `/{post_id}/like` | Like/Unlike | Yes |
| POST | `/{post_id}/comment` | Bình luận | Yes |

### 3.5 Admin `/api/v1/admin` (role_id = 1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Thống kê tổng quan |
| GET | `/users` | Quản lý users |
| PATCH | `/users/{id}/ban` | Ban user |
| GET/POST/PUT/DELETE | `/posts/*` | Quản lý bài viết |
| GET/POST/PUT/DELETE | `/places/*` | Quản lý địa điểm |
| GET/POST | `/reports/*` | Xử lý báo cáo |

### 3.6 Chatbot `/api/v1/chatbot`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/message` | Gửi tin nhắn AI | Yes |
| GET | `/history` | Lịch sử chat | Yes |
| GET | `/health` | Health check | No |

### 3.7 Upload `/api/v1/upload`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/` | Upload files | Yes |

**Params:** `files` (max 10), `folder` (places/avatars/posts/misc)

---

## 4. Authentication

### JWT Token

```
Authorization: Bearer <access_token>
```

| Token | TTL | Purpose |
|-------|-----|---------|
| Access | 1 hour | API requests |
| Refresh | 7 days | Renew access token |

### Role-Based Access

| role_id | Role | Quyền hạn |
|---------|------|-----------|
| 1 | admin | Full access |
| 2 | moderator | Content moderation |
| 3 | user | Standard access |

---

## 5. Rate Limiting

| Tier | Requests/Min | Endpoints |
|------|--------------|-----------|
| high | 5 | Login, Register |
| medium | 20 | Post, Comment |
| low | 60 | GET requests |

---

## 6. Response Format

### Success
```json
{
  "success": true,
  "message": "...",
  "data": {...}
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "..."
  }
}
```

---

## 7. Environment Variables

### Required

```bash
# Database
DATABASE_URL=postgresql://...
MONGO_URI=mongodb://...

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION=3600

# Server
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8080
```

### Optional

```bash
# Email
SENDGRID_API_KEY=...
FROM_EMAIL=...

# AI Chatbot
CHATBOT_API_KEY=...
CHATBOT_MODEL=...

# AWS S3
USE_S3=true
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=...

# Rate Limiting
RATE_LIMIT_ENABLED=true
THROTTLE_ENABLED=true
```

---

## 8. Chạy Server

### Development
```bash
cd src/backend
python run.py
```

### Production
```bash
python run.py --prod
```

### URLs
- API: `http://localhost:8080`
- Swagger: `http://localhost:8080/docs`

---

## 9. Error Codes

| Code | Description |
|------|-------------|
| INVALID_CREDENTIALS | Sai email/password |
| INVALID_TOKEN | Token không hợp lệ |
| USER_BANNED | Tài khoản bị khóa |
| RATE_LIMIT_EXCEEDED | Quá số lượng request |
| FORBIDDEN | Không có quyền |
| NOT_FOUND | Không tìm thấy |

---

*Author: Hoang Van Phu | Project: Hanoivivu*
