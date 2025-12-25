# 🐳 Hướng dẫn Cài đặt & Vận hành Hệ thống (Docker Local)

Tài liệu này hướng dẫn chi tiết các bước khởi chạy môi trường **PostgreSQL Database**, **pgAdmin 4** và **Backend API** sử dụng Docker Compose.

## 🛠 Yêu cầu hệ thống (Prerequisites)

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Đã cài đặt và trạng thái **Running**).
* [Git](https://git-scm.com/) (Để clone source code).
* Tài khoản Google (Để tải folder uploads từ Google Drive).

---

## 🚀 Các bước cài đặt (Quick Start)

### Bước 1: Kiểm tra Docker

Mở terminal và gõ lệnh sau để chắc chắn Docker đã sẵn sàng:

```bash
docker --version
```

### Bước 2: Clone dự án & Di chuyển thư mục

Tải source code về máy và đi vào thư mục chứa file `docker-compose.yml`:

```bash
# 1. Clone repository (Thay link repo của bạn vào đây)
git clone <link-repo-cua-ban>

# 2. Di chuyển vào thư mục source
cd src
```

### Bước 3: Tải folder uploads từ Google Drive

⚠️ **QUAN TRỌNG:** Folder `uploads` chứa các ảnh của hệ thống, cần được tải về trước khi khởi chạy Backend.

#### 3.1. Truy cập Google Drive:

Mở trình duyệt và truy cập link sau:
```
https://drive.google.com/drive/folders/1Uiwnk4nNdChMOJ7KBU-RXgCdQ4t4heTI?usp=sharing
```

#### 3.2. Tải folder uploads:

**Cách 1: Tải trực tiếp từ Google Drive (Khuyến nghị)**
1. Click chuột phải vào folder `uploads` trong Google Drive
2. Chọn **"Download"** hoặc **"Tải xuống"**
3. Giải nén file ZIP vừa tải về
4. Di chuyển folder `uploads` vào thư mục `src` (cùng cấp với file `docker-compose.yml`)

**Cách 2: Sử dụng Google Drive Desktop (Nếu có)**
1. Đồng bộ folder từ Google Drive về máy
2. Copy folder `uploads` vào thư mục `src`

#### 3.3. Kiểm tra cấu trúc thư mục:

Sau khi tải xong, cấu trúc thư mục `src` phải như sau:

```
src/
├── docker-compose.yml
├── uploads/              ← Folder này phải có
│   └── places/
│       └── ... (các file ảnh)
├── backend/
├── database/
└── ...
```

### Bước 4: Xóa Database cũ (Nếu có) - ⚠️ QUAN TRỌNG

Nếu bạn đã từng chạy Docker Compose trước đó và muốn **reset lại database từ đầu**, cần xóa Volume cũ:

```bash
# Dừng và xóa tất cả containers, networks và volumes
docker-compose down -v
```

⚠️ **Cảnh báo:** Lệnh này sẽ **xóa sạch toàn bộ dữ liệu** trong database. Chỉ chạy khi bạn muốn khởi tạo lại từ đầu.

**Khi nào cần chạy `down -v`:**
- Lần đầu tiên setup hệ thống
- Khi file `init.sql` được cập nhật và bạn muốn nạp lại dữ liệu mới
- Khi gặp lỗi dữ liệu và cần reset lại

**Khi KHÔNG cần chạy `down -v`:**
- Chỉ muốn restart lại containers
- Chỉ cập nhật code Backend (không thay đổi DB)

### Bước 5: Tạo file .env (Nếu chưa có)

Tạo file `.env` trong thư mục `src` với nội dung mẫu sau (hoặc sử dụng file `.env.example` nếu có):

```env
# Database Configuration
POSTGRES_USER=admin
POSTGRES_PASSWORD=Secure_Pass_2025!
POSTGRES_DB=travel_db
DB_PORT=5433

# pgAdmin Configuration
PGADMIN_EMAIL=admin@travel.com
PGADMIN_PASSWORD=admin123
PGADMIN_PORT=5050

# Backend Configuration
BACKEND_PORT=8000
```

### Bước 6: Build và Khởi chạy (Build & Run)

Sử dụng Docker Compose để dựng toàn bộ hệ thống (Database + pgAdmin + Backend).
Lệnh này sẽ tự động nạp dữ liệu từ file `init.sql` trong lần chạy đầu tiên.

```bash
docker-compose up -d --build
```

**Giải thích các tham số:**
- `up`: Khởi động containers.
- `-d`: Detached mode (Chạy ngầm, không giữ terminal).
- `--build`: Buộc build lại image để cập nhật code/sql mới nhất.

⏳ **Lưu ý:** Lần chạy đầu tiên có thể mất 1-2 phút để:
- Build images
- Khởi tạo Database
- Nạp dữ liệu từ `init.sql`
- Khởi động Backend API

Vui lòng đợi đến khi log báo "database system is ready" và Backend khởi động thành công.

### Bước 7: Kiểm tra trạng thái containers

Kiểm tra xem tất cả containers đã chạy thành công chưa:

```bash
docker ps
```

Bạn sẽ thấy 3 containers đang chạy:
- `travel_db_container` (PostgreSQL)
- `travel_pgadmin_container` (pgAdmin 4)
- `travel_backend_container` (Backend API)

---

## 🔌 Thông tin Kết nối (Connection Reference)

Bảng thông tin dùng để cấu hình Backend hoặc kết nối bằng Tool (DBeaver, TablePlus, pgAdmin Local):

| Service | Host | Port (External) | User | Password | Database |
|---------|------|-----------------|------|----------|----------|
| PostgreSQL | localhost | 5433 | admin | Secure_Pass_2025! | travel_db |
| pgAdmin (Web) | localhost | 5050 | admin@travel.com | admin123 | - |
| Backend API | localhost | 8000 | - | - | - |

**Lưu ý quan trọng:**
- Khi config trong **pgAdmin (Web)**, Host name của DB phải là: `db` (Port 5432).
- Khi config trong **Code Backend (Local)**, Host name của DB là: `localhost` (Port 5433).
- Khi config trong **Backend Container**, Host name của DB là: `db` (Port 5432) - đã được cấu hình sẵn trong `docker-compose.yml`.

---

## 🧪 Test luồng lấy ảnh từ Database

Sau khi hệ thống đã khởi động thành công, bạn có thể test API lấy ảnh từ Database.

### 7.1. Kiểm tra Backend đang chạy:

Mở trình duyệt hoặc dùng `curl` để test endpoint:

```bash
# Test endpoint root
curl http://localhost:8000/

# Hoặc mở trình duyệt và truy cập:
# http://localhost:8000/
```

Kết quả mong đợi:
```json
{
  "message": "Hanoi Travel Test Backend is Running form tests/database!"
}
```

### 7.2. Test API lấy danh sách địa điểm có ảnh:

```bash
# Sử dụng curl
curl http://localhost:8000/test-places

# Hoặc mở trình duyệt và truy cập:
# http://localhost:8000/test-places
```

**Kết quả mong đợi:**
```json
[
  {
    "id": 1,
    "name": "Tên địa điểm",
    "db_path": "/static/uploads/places/ten-file.jpg",
    "test_link": "http://localhost:8000/static/uploads/places/ten-file.jpg"
  },
  ...
]
```

### 7.3. Test truy cập ảnh trực tiếp:

Sau khi có `test_link` từ API trên, mở link đó trong trình duyệt để xem ảnh:

```
http://localhost:8000/static/uploads/places/ten-file.jpg
```

**Lưu ý:**
- Nếu ảnh hiển thị thành công → ✅ Hệ thống hoạt động đúng
- Nếu ảnh không hiển thị (404 Not Found) → Kiểm tra:
  1. Folder `uploads` đã được tải về và đặt đúng vị trí trong `src/`
  2. Volume mapping trong `docker-compose.yml` đã đúng: `./uploads:/app/static/uploads`
  3. Tên file trong Database khớp với tên file thực tế trong folder `uploads`

### 7.4. Kiểm tra log Backend (Nếu có lỗi):

```bash
docker logs travel_backend_container
```

---

## 📋 Demo Kết nối Database & Truy vấn (Verification)

Sử dụng giao diện dòng lệnh (CLI) để kiểm tra nhanh dữ liệu bên trong Container.

### 8.1. Truy cập vào PostgreSQL CLI:

```bash
docker exec -it travel_db_container psql -U admin -d travel_db
```

(Khi thành công, dấu nhắc lệnh sẽ đổi thành: `travel_db=#`)

### 8.2. Hiển thị danh sách bảng:

```sql
\dt
```

### 8.3. Chạy thử câu truy vấn mẫu:

```sql
-- Đếm tổng số user hiện có
SELECT COUNT(*) FROM users;

-- Xem thông tin 5 khách sạn đầu tiên
SELECT * FROM hotels LIMIT 5;

-- Xem các địa điểm có ảnh
SELECT p.id, p.name, pi.image_url 
FROM places p 
JOIN place_images pi ON p.id = pi.place_id 
WHERE pi.is_main = true 
LIMIT 5;
```

### 8.4. Thoát khỏi CLI:

```sql
\q
```

---

## ❓ Xử lý sự cố (Troubleshooting)

### 1. Dữ liệu không cập nhật dù đã sửa file init.sql?

Docker lưu dữ liệu cũ trong Volume. Để cập nhật lại từ đầu, cần xóa Volume cũ:

```bash
# ⚠️ CẢNH BÁO: Xóa sạch dữ liệu cũ
docker-compose down -v
docker-compose up -d --build
```

### 2. Lỗi "Connection Refused" hoặc không vào được pgAdmin/Backend?

Kiểm tra xem container có đang chạy không:

```bash
docker ps
```

Nếu không thấy container, xem log lỗi:

```bash
# Log của Database
docker logs travel_db_container

# Log của Backend
docker logs travel_backend_container

# Log của pgAdmin
docker logs travel_pgadmin_container
```

### 3. Ảnh không hiển thị khi truy cập qua API?

**Nguyên nhân thường gặp:**
- Folder `uploads` chưa được tải về hoặc đặt sai vị trí
- Volume mapping không đúng
- Tên file trong Database không khớp với file thực tế

**Cách kiểm tra:**

```bash
# 1. Kiểm tra folder uploads có tồn tại trong src/
ls -la src/uploads

# 2. Kiểm tra volume mapping trong container
docker exec -it travel_backend_container ls -la /app/static/uploads

# 3. Kiểm tra log Backend để xem lỗi chi tiết
docker logs travel_backend_container
```

### 4. Port đã được sử dụng (Port already in use)?

Nếu gặp lỗi port đã được sử dụng, bạn có thể:

**Cách 1:** Thay đổi port trong file `.env`:
```env
DB_PORT=5434          # Thay vì 5433
PGADMIN_PORT=5051     # Thay vì 5050
BACKEND_PORT=8001     # Thay vì 8000
```

**Cách 2:** Dừng service đang sử dụng port đó.

### 5. Container không build được?

```bash
# Xóa image cũ và build lại
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 Tóm tắt các lệnh thường dùng

```bash
# Khởi động hệ thống
docker-compose up -d --build

# Dừng hệ thống (giữ lại data)
docker-compose down

# Dừng và xóa toàn bộ data (reset)
docker-compose down -v

# Xem log real-time
docker-compose logs -f

# Xem log của service cụ thể
docker logs travel_backend_container
docker logs travel_db_container

# Restart một service cụ thể
docker-compose restart backend

# Rebuild lại một service
docker-compose up -d --build backend
```

---

## ✅ Checklist trước khi chạy

- [ ] Docker Desktop đã được cài đặt và đang chạy
- [ ] Đã clone repository về máy
- [ ] Đã tải folder `uploads` từ Google Drive và đặt vào `src/`
- [ ] Đã tạo file `.env` với các biến môi trường cần thiết
- [ ] Đã chạy `docker-compose down -v` (nếu muốn reset database)
- [ ] Đã chạy `docker-compose up -d --build`
- [ ] Đã kiểm tra 3 containers đang chạy bằng `docker ps`
- [ ] Đã test API tại `http://localhost:8000/test-places`
- [ ] Đã kiểm tra ảnh hiển thị thành công

---

**Chúc bạn setup thành công! 🎉**
