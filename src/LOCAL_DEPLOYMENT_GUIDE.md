# Hướng Dẫn Deploy Local (Docker)

Hướng dẫn deploy ứng dụng Hanoi Travel trên máy local sử dụng Docker.

## Yêu cầu

- **Docker Desktop** đã cài đặt và đang chạy
- **Git** (để clone repo nếu cần)
- File `.env.prod` với đầy đủ cấu hình

---

## Quick Start

```powershell
# 1. Mở Docker Desktop (bắt buộc)

# 2. Vào thư mục src
cd D:\CSDL_Web\WEB_Final\src

# 3. Build và chạy
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# 4. Kiểm tra
docker ps
```

---

## Các bước chi tiết

### Bước 1: Khởi động Docker Desktop

Đảm bảo Docker Desktop đang chạy (icon Docker xuất hiện ở system tray).

### Bước 2: Chuẩn bị file môi trường

Đảm bảo file `.env.prod` tồn tại trong thư mục `src/` với các biến sau:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres123456@travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com:5434/travel_db

# S3
UPLOADS_BASE_URL=https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads

# MongoDB
MONGO_URI=mongodb+srv://...

# Security
JWT_SECRET_KEY=your-secret-key
SESSION_SECRET=your-session-secret

# API
VITE_API_URL=/api/v1

# Chatbot
CHATBOT_API_KEY=your-gemini-api-key

# Email Validation
HUNTER_IO_API_KEY=your-hunter-api-key
```

### Bước 3: Build Docker Images

```powershell
cd D:\CSDL_Web\WEB_Final\src

# Build tất cả images
docker compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache
```

**Thời gian**: ~3-5 phút (lần đầu)

### Bước 4: Chạy Containers

```powershell
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Bước 5: Kiểm tra

```powershell
# Xem containers đang chạy
docker ps

# Kết quả mong đợi:
# travel_frontend_prod   Up (healthy)   0.0.0.0:80->80/tcp
# travel_backend_prod    Up (healthy)   0.0.0.0:8000->8000/tcp
```

---

## Truy cập ứng dụng

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## Các lệnh thường dùng

```powershell
# Xem logs
docker logs travel_backend_prod -f
docker logs travel_frontend_prod -f

# Restart
docker compose -f docker-compose.prod.yml --env-file .env.prod restart

# Stop
docker compose -f docker-compose.prod.yml --env-file .env.prod down

# Rebuild và chạy lại
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Xóa sạch và build lại
docker compose -f docker-compose.prod.yml --env-file .env.prod down -v
docker system prune -af
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

---

## Xử lý lỗi thường gặp

### Lỗi: "gunicorn: executable file not found"

**Nguyên nhân**: requirements.txt thiếu gunicorn

**Cách fix**:
```powershell
# Thêm vào src/backend/requirements.txt
gunicorn>=21.0.0

# Rebuild
docker compose -f docker-compose.prod.yml --env-file .env.prod build backend --no-cache
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Lỗi: "CHATBOT_API_KEY variable is not set"

**Nguyên nhân**: Thiếu biến trong .env.prod

**Cách fix**: Thêm biến vào `.env.prod`:
```env
CHATBOT_API_KEY=AIzaSy...
```

### Lỗi: Container không start được

**Cách debug**:
```powershell
# Xem logs chi tiết
docker logs travel_backend_prod

# Xem container đã exit
docker ps -a
```

### Lỗi: Port 80 đã được sử dụng

**Cách fix**:
```powershell
# Tìm process đang dùng port 80
netstat -ano | findstr :80

# Hoặc đổi port trong docker-compose.prod.yml
ports:
  - "8080:80"  # Thay 80 thành 8080
```

---

## Chạy với Ngrok (Public URL)

```powershell
# Cấu hình ngrok (lần đầu)
ngrok config add-authtoken YOUR_TOKEN

# Chạy tunnel
ngrok http 80

# Kết quả: https://xxxx.ngrok-free.app
```
