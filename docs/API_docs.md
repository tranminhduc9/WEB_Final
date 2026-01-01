# Hanoivivu API Documentation

**Base URL:** `http://127.0.0.1:8080/api/v1`

**Swagger UI:** `http://127.0.0.1:8080/docs`

---

## Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Đăng ký user mới | 🔓 Public |
| POST | `/auth/login` | Đăng nhập | 🔓 Public |
| POST | `/auth/refresh` | Refresh access token | 🔓 Public |
| POST | `/auth/logout` | Đăng xuất | 🔓 Public |
| GET | `/auth/verify-email` | Xác thực email (query: token) | 🔓 Public |
| GET | `/auth/me` | Lấy thông tin user hiện tại | 🔐 Required |

### Request/Response Examples

<details>
<summary>POST /auth/register</summary>

```json
// Request
{
  "full_name": "Nguyễn Văn A",
  "email": "example@gmail.com",
  "password": "abc123"
}

// Response 201
{
  "success": true,
  "message": "Đăng ký thành công",
  "user": { "id": 1, "email": "...", "full_name": "..." }
}
```
</details>

<details>
<summary>POST /auth/login</summary>

```json
// Request
{
  "email": "example@gmail.com",
  "password": "abc123"
}

// Response 200
{
  "success": true,
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "role_id": 1 }
}
```
</details>

---

## Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me` | Lấy profile của user hiện tại | 🔐 Required |
| PUT | `/users/me` | Cập nhật profile | 🔐 Required |
| PUT | `/users/change-password` | Đổi mật khẩu | 🔐 Required |
| GET | `/users/{user_id}` | Lấy thông tin public của user khác | 🔓 Public |
| GET | `/profile` | Alias cho /users/me | 🔐 Required |
| PUT | `/profile` | Alias cho PUT /users/me | 🔐 Required |
| POST | `/users/avatar` | Upload avatar | 🔐 Required |
| DELETE | `/users/avatar` | Xóa avatar | 🔐 Required |
| DELETE | `/users/favorites/{place_id}` | Xóa địa điểm yêu thích | 🔐 Required |

---

## Places

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/places` | Danh sách địa điểm (có filter) | 🔓 Public |
| GET | `/places/search` | Tìm kiếm địa điểm | 🔓 Public |
| GET | `/places/suggestions` | Gợi ý tìm kiếm (autocomplete) | 🔓 Public |
| GET | `/places/nearby` | Địa điểm lân cận (lat, long, radius) | 🔓 Public |
| GET | `/places/districts` | Danh sách quận/huyện | 🔓 Public |
| GET | `/places/types` | Danh sách loại địa điểm | 🔓 Public |
| GET | `/places/{place_id}` | Chi tiết địa điểm | 🔓 Public |
| POST | `/places/{place_id}/favorite` | Toggle yêu thích địa điểm | 🔐 Required |

### Query Parameters

**GET /places:**
- `page` (int): Số trang (default: 1)
- `limit` (int): Số lượng/trang (default: 10, max: 50)
- `district_id` (int): Filter theo quận
- `place_type_id` (int): Filter theo loại

**GET /places/search:**
- `keyword` (string): Từ khóa tìm kiếm
- `district_id`, `place_type_id`: Bộ lọc
- `page`, `limit`: Phân trang

---

## Posts

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/posts` | Danh sách bài viết (feed) | 🔓 Public |
| POST | `/posts` | Tạo bài viết mới (pending approval) | 🔐 Required |
| GET | `/posts/{post_id}` | Chi tiết bài viết | 🔓 Public |
| DELETE | `/posts/{post_id}` | Xóa bài viết của mình | 🔐 Required |
| POST | `/posts/{post_id}/like` | Toggle like bài viết | 🔐 Required |
| POST | `/posts/{post_id}/comment` | Thêm comment | 🔐 Required |
| POST | `/posts/{post_id}/favorite` | Toggle favorite bài viết | 🔐 Required |
| POST | `/posts/{post_id}/report` | Báo cáo bài viết | 🔐 Required |
| POST | `/comments/{comment_id}/reply` | Reply comment | 🔐 Required |
| DELETE | `/comments/{comment_id}` | Xóa comment | 🔐 Required |
| POST | `/comments/{comment_id}/report` | Báo cáo comment | 🔐 Required |

### Request Examples

<details>
<summary>POST /posts</summary>

```json
{
  "title": "Review Phở Thìn",
  "content": "Nội dung bài viết...",
  "images": ["/static/uploads/posts/img1.jpg"],
  "tags": ["food", "hanoi"],
  "related_place_id": 123,
  "rating": 4.5
}
```
</details>

---

## Chatbot

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/chatbot/message` | Gửi tin nhắn đến AI chatbot | 🔐 Required |
| GET | `/chatbot/history` | Lấy lịch sử chat | 🔐 Required |

---

## Upload

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/upload` | Upload files (images) | 🔐 Required |

**Parameters:**
- `files`: Danh sách files (multipart/form-data)
- `folder`: Subfolder (default: "misc")
- `upload_type`: "place" | "avatar" | "post" | "generic"
- `entity_id`: ID liên quan (required nếu upload_type != generic)

**Supported formats:** PNG, JPG, JPEG, GIF, WEBP (max 10MB/file)

---

## System Logs (Admin only)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/logs/audit` | Lấy audit logs từ database | 🔒 Admin |
| GET | `/logs/app` | Lấy application logs | 🔒 Admin |
| GET | `/logs/stats` | Thống kê về logs | 🔒 Admin |
| GET | `/logs/visits` | Visit logs | 🔒 Admin |
| GET | `/logs/analytics` | Thống kê tổng hợp cho dashboard | 🔒 Admin |

---

## Admin Panel

> **Tất cả endpoint admin yêu cầu role_id = 1 (Admin)**

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/dashboard` | Thống kê dashboard |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | Danh sách users |
| DELETE | `/admin/users/{user_id}` | Xóa user (soft delete) |
| PATCH | `/admin/users/{user_id}/ban` | Ban user |
| PATCH | `/admin/users/{user_id}/unban` | Unban user |

### Post Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/posts` | Danh sách posts |
| POST | `/admin/posts` | Tạo post (auto-approved) |
| PUT | `/admin/posts/{post_id}` | Cập nhật post |
| DELETE | `/admin/posts/{post_id}` | Xóa post |
| PATCH | `/admin/posts/{post_id}/status` | Approve/Reject post |

### Comment Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/comments` | Danh sách comments |
| DELETE | `/admin/comments/{comment_id}` | Xóa comment |

### Report Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/reports` | Danh sách reports |

### Place Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/places` | Danh sách places |
| POST | `/admin/places` | Tạo place mới |
| PUT | `/admin/places/{place_id}` | Cập nhật place |
| DELETE | `/admin/places/{place_id}` | Xóa place (soft delete) |

### Rating Sync
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/sync-ratings` | Đồng bộ rating tất cả places |
| POST | `/admin/places/{place_id}/sync-rating` | Đồng bộ rating cho 1 place |

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Thông báo thành công",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mô tả lỗi"
  }
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Email hoặc mật khẩu không đúng |
| `UNAUTHORIZED` | 401 | Chưa đăng nhập |
| `FORBIDDEN` | 403 | Không có quyền truy cập |
| `NOT_FOUND` | 404 | Không tìm thấy resource |
| `VALIDATION_ERROR` | 422 | Dữ liệu không hợp lệ |
| `TOO_MANY_REQUESTS` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Lỗi server |

---

## Authentication

API sử dụng **JWT Bearer Token** cho authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

**Token Expiry:**
- Access Token: 30 phút
- Refresh Token: 7 ngày

---

## Rate Limiting

- **Login:** 5 lần/phút
- **Register:** 3 lần/phút  
- **API calls:** 100 lần/phút (per IP)
