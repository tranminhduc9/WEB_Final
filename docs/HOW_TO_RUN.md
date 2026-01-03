# 🐳 Hướng dẫn Chạy với Docker

> **Yêu cầu:** Cài đặt Docker trước khi bắt đầu → [Hướng dẫn cài Docker](#cài-đặt-docker)

---

## Các bước chạy

### 1. Tạo file `.env`

```bash
cd src
cp .env.example .env
```

### 2. Điền các biến môi trường trong `.env`

Mở file `.env` và cập nhật các giá trị sau:

```env
# Database PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/travel_db

# MongoDB
MONGO_URI=mongodb://localhost:27017/hanoi_travel

# JWT Secret (đổi thành chuỗi bí mật của bạn)
JWT_SECRET_KEY=your-secret-key-at-least-32-characters
SESSION_SECRET=your-session-secret-key

# (Tùy chọn) AWS S3 - nếu dùng S3 cho ảnh
USE_S3=false
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name

# (Tùy chọn) SendGrid - nếu dùng gửi email
SENDGRID_API_KEY=your-sendgrid-api-key

# (Tùy chọn) AI Chatbot
CHATBOT_API_KEY=your-gemini-api-key
```

### 3. Build và chạy

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

### 4. Kiểm tra

```bash
# Xem containers đang chạy
docker ps

# Mở trình duyệt
# Frontend: http://localhost
# Backend API: http://localhost:8080/docs
```

---

## Các lệnh thường dùng

```bash
# Dừng hệ thống
docker compose -f docker-compose.prod.yml --env-file .env down

# Xem logs
docker compose -f docker-compose.prod.yml --env-file .env logs -f

# Restart
docker compose -f docker-compose.prod.yml --env-file .env restart

# Rebuild lại
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

---

## Cài đặt Docker

### Windows / Mac

1. Tải [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Cài đặt và khởi động Docker Desktop
3. Kiểm tra: `docker --version`

### Ubuntu/Debian

```bash
# Cài đặt
curl -fsSL https://get.docker.com | sudo sh

# Thêm user vào group docker
sudo usermod -aG docker $USER

# Khởi động lại terminal, sau đó kiểm tra
docker --version
```

---

**Xong!** Truy cập http://localhost để sử dụng.
