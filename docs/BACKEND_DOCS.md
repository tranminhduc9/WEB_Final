# Hanoivivu Backend Documentation

> **Author:** Hoàng Văn Phú | **Version:** 1.1.0 | **Last Updated:** 2026-01-02

---

## 🚀 Quick Start

```bash
cd src/backend
pip install -r requirements.txt
python run.py --reload  # Development
```

**Base URL:** `http://127.0.0.1:8080/api/v1` | **Swagger:** `http://127.0.0.1:8080/docs`

---

## 🔗 API Endpoints

**Auth Legend:** 🔓 Public | 🔐 Login Required | 🔒 Admin Only

### Authentication `/auth`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| POST | `/register` | Đăng ký user | 🔓 |
| POST | `/login` | Đăng nhập | 🔓 |
| POST | `/refresh` | Refresh token | 🔓 |
| POST | `/logout` | Đăng xuất | 🔓 |
| GET | `/verify-email?token=` | Xác thực email | 🔓 |
| GET | `/me` | Thông tin user hiện tại | 🔐 |
| POST | `/forgot-password` | Quên mật khẩu | 🔓 |
| POST | `/reset-password` | Reset mật khẩu | 🔓 |

### Users `/users`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| GET | `/me` | Lấy profile | 🔐 |
| PUT | `/me` | Cập nhật profile | 🔐 |
| PUT | `/change-password` | Đổi mật khẩu | 🔐 |
| GET | `/{user_id}` | Public info của user | 🔓 |
| GET | `/profile` | Alias `/me` | 🔐 |
| PUT | `/profile` | Alias PUT `/me` | 🔐 |
| POST | `/avatar` | Upload avatar | 🔐 |
| DELETE | `/avatar` | Xóa avatar | 🔐 |
| DELETE | `/me/favorites/places/{place_id}` | Xóa địa điểm yêu thích | 🔐 |

### Places `/places`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| GET | `/` | Danh sách (filter: `district_id`, `place_type_id`, `page`, `limit`) | 🔓 |
| GET | `/search` | Tìm kiếm (`keyword`) | 🔓 |
| GET | `/suggest` | Autocomplete suggestions | 🔓 |
| GET | `/nearby` | Lân cận (`lat`, `long`, `radius`) | 🔓 |
| GET | `/districts` | Danh sách quận | 🔓 |
| GET | `/place-types` | Loại địa điểm | 🔓 |
| GET | `/{place_id}` | Chi tiết | 🔓 |
| POST | `/{place_id}/favorite` | Toggle yêu thích | 🔐 |

### Posts (prefix: none, routes có `/posts` và `/comments`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| GET | `/posts` | Feed bài viết | 🔓 |
| POST | `/posts` | Tạo bài viết | 🔐 |
| GET | `/posts/{post_id}` | Chi tiết bài viết | 🔓 |
| DELETE | `/posts/{post_id}` | Xóa bài viết của mình | 🔐 |
| POST | `/posts/{post_id}/like` | Toggle like | 🔐 |
| POST | `/posts/{post_id}/comments` | Thêm comment | 🔐 |
| POST | `/posts/{post_id}/favorite` | Toggle favorite | 🔐 |
| POST | `/posts/{post_id}/report` | Báo cáo bài viết | 🔐 |
| POST | `/comments/{comment_id}/reply` | Reply comment | 🔐 |
| DELETE | `/comments/{comment_id}` | Xóa comment | 🔐 |
| POST | `/comments/{comment_id}/report` | Báo cáo comment | 🔐 |

### Upload `/upload`
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| POST | `/` | Upload images (PNG/JPG/GIF/WEBP, max 10MB) | 🔐 |

---

## 🤖 Chatbot `/chatbot`

**AI:** Google Gemini | **Features:** Place context injection, Conversation history, Smart suggestions (max 3)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|:----:|
| POST | `/message` | Gửi tin nhắn | 🔐 |
| GET | `/history` | Lịch sử chat (`conversation_id`, `limit`) | 🔐 |
| GET | `/health` | Health check | 🔓 |

**POST /message:**
```json
// Request
{ "message": "Tìm quán phở ngon ở Hoàn Kiếm", "conversation_id": "optional-uuid" }

// Response
{ "success": true, "conversation_id": "uuid", "bot_response": "...", "suggested_places": [...] }
```

**Architecture:** `User Message → PlaceContextService (PostgreSQL) → GeminiService (AI) → MongoDB (save logs)`

---

## 🔒 Admin `/admin`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Thống kê dashboard |
| GET | `/users` | Danh sách users |
| DELETE | `/users/{id}` | Xóa user (soft delete) |
| PATCH | `/users/{id}/ban` | Ban user |
| PATCH | `/users/{id}/unban` | Unban user |
| GET | `/posts` | Danh sách posts |
| POST | `/posts` | Tạo post (auto-approved) |
| PUT | `/posts/{id}` | Cập nhật post |
| DELETE | `/posts/{id}` | Xóa post |
| PATCH | `/posts/{id}/status` | Approve/Reject |
| GET | `/comments` | Danh sách comments |
| DELETE | `/comments/{id}` | Xóa comment |
| GET | `/reports` | Danh sách reports |
| GET | `/places` | Danh sách places |
| POST | `/places` | Tạo place |
| PUT | `/places/{id}` | Cập nhật place |
| DELETE | `/places/{id}` | Xóa place |
| POST | `/sync-ratings` | Sync all ratings |
| POST | `/places/{id}/sync-rating` | Sync single rating |

### Logs `/logs` (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit` | Audit logs |
| GET | `/app` | Application logs |
| GET | `/stats` | Log statistics |
| GET | `/visits` | Visit logs |
| GET | `/analytics` | Dashboard analytics |

---

## 📦 Response Format

```json
// Success
{ "success": true, "message": "...", "data": {...} }

// Error
{ "success": false, "error": { "code": "ERROR_CODE", "message": "..." } }
```

**Error Codes:** `UNAUTHORIZED(401)` | `FORBIDDEN(403)` | `NOT_FOUND(404)` | `VALIDATION_ERROR(422)` | `TOO_MANY_REQUESTS(429)`

---

## 🔐 Authentication

**JWT Bearer Token** | Access: 30 phút | Refresh: 7 ngày

```
Authorization: Bearer <access_token>
```

---

## ⚡ Rate Limiting

| Endpoint | Limit |
|----------|-------|
| Login/Register | 5/3 req/min |
| Chatbot | 20 req/min |
| General | 100 req/min |

---

## 🗄️ Database

**PostgreSQL:** `users`, `places`, `districts`, `place_types`, `ratings`, `favorites`

**MongoDB:** `posts_mongo`, `post_likes_mongo`, `post_comments_mongo`, `chatbot_logs_mongo`, `reports_mongo`

---

## 📁 Project Structure

```
src/backend/
├── app/
│   ├── api/v1/        # Routes: auth, users, places, posts, chatbot, upload, admin, logs
│   ├── chatbot/       # AI: gemini_service, place_context, prompts, config
│   ├── services/      # Business: auth_service, rating_sync, post_stats_sync, logging_service
│   └── utils/         # Helpers: timezone, image, place
├── config/            # database, settings, load_env, image_config
├── middleware/        # auth, mongodb_client, rate_limit, cors, email_service, error_handler, validator, throttle, secure_cookies
├── run.py             # Entry point
└── requirements.txt
```

---

## 🔧 Environment (.env)

```env
DATABASE_URL=postgresql://user:pass@localhost:5433/hanoivivu
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=hanoivivu_mongo
JWT_SECRET_KEY=your-secret
GEMINI_API_KEY=your-gemini-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-app-password
```
