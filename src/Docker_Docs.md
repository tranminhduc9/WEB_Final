# 🐳 Hướng dẫn Cài đặt & Vận hành Database (Docker Local)

Tài liệu này hướng dẫn chi tiết các bước khởi chạy môi trường Database PostgreSQL 17 và pgAdmin 4 sử dụng Docker Compose.

## 🛠 Yêu cầu hệ thống (Prerequisites)

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Đã cài đặt và trạng thái **Running**).
* [Git](https://git-scm.com/) (Để clone source code).

---

## 🚀 Các bước cài đặt (Quick Start)

### Bước 1: Kiểm tra Docker

Mở terminal và gõ lệnh sau để chắc chắn Docker đã sẵn sàng:

```bash
docker --version
```

### Bước 2: Clone dự án & Di chuyển thư mục

Tải source code về máy và đi vào thư mục chứa file docker-compose.yml (thường là thư mục src hoặc database):

```bash
# 1. Clone repository (Thay link repo của bạn vào đây)
git clone <link-repo-cua-ban>
# 
# 2. Di chuyển vào thư mục source
cd src
```

### Bước 3 & 4: Build và Khởi chạy (Build & Run)

Sử dụng Docker Compose để dựng toàn bộ hệ thống (Database + pgAdmin).
Lệnh này sẽ tự động nạp dữ liệu từ file init.sql trong lần chạy đầu tiên.

```bash
docker-compose up -d --build
```

**Giải thích các tham số:**
- `up`: Khởi động containers.
- `-d`: Detached mode (Chạy ngầm, không giữ terminal).
- `--build`: Buộc build lại image để cập nhật code/sql mới nhất.

⏳ **Lưu ý:** Lần chạy đầu tiên có thể mất 30s - 1 phút để Database khởi tạo. Vui lòng đợi đến khi log báo "database system is ready".

### Bước 5: Demo Kết nối & Truy vấn (Verification)

Sử dụng giao diện dòng lệnh (CLI) để kiểm tra nhanh dữ liệu bên trong Container.

#### 5.1. Truy cập vào PostgreSQL CLI:

```bash
docker exec -it travel_db_container psql -U admin -d travel_db
```

(Khi thành công, dấu nhắc lệnh sẽ đổi thành: `travel_db=#`)

#### 5.2. Hiển thị danh sách bảng:

```sql
\dt
```

#### 5.3. Chạy thử câu truy vấn mẫu:

```sql
-- Đếm tổng số user hiện có
SELECT COUNT(*) FROM users;

-- Xem thông tin 5 khách sạn đầu tiên
SELECT * FROM hotels LIMIT 5;
```

#### 5.4. Thoát khỏi CLI:

```sql
\q
```

---

## 🔌 Thông tin Kết nối (Connection Reference)

Bảng thông tin dùng để cấu hình Backend hoặc kết nối bằng Tool (DBeaver, TablePlus, pgAdmin Local):

| Service | Host | Port (External) | User | Password | Database |
|---------|------|-----------------|------|----------|----------|
| PostgreSQL | localhost | 5433 | admin | Secure_Pass_2025! | travel_db |
| pgAdmin (Web) | localhost | 5050 | admin@travel.com | admin123 | - |

**Lưu ý quan trọng:**
- Khi config trong pgAdmin (Web), Host name của DB phải là: `db` (Port 5432).
- Khi config trong Code Backend (Local), Host name của DB là: `localhost` (Port 5433).

---

## ❓ Xử lý sự cố (Troubleshooting)

### 1. Dữ liệu không cập nhật dù đã sửa file init.sql?

Docker lưu dữ liệu cũ trong Volume. Để cập nhật lại từ đầu, cần xóa Volume cũ:

```bash
docker-compose down -v
docker-compose up -d --build
```

⚠️ **Cảnh báo:** Lệnh này xóa sạch dữ liệu cũ.

### 2. Lỗi "Connection Refused" hoặc không vào được pgAdmin?

Kiểm tra xem container có đang chạy không:

```bash
docker ps
```

Nếu không thấy container, xem log lỗi:

```bash
docker logs travel_db_container
```
