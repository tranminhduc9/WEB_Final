# 🚀 AWS Deployment Guide - Travel Web Application

Hướng dẫn đầy đủ triển khai ứng dụng từ Local Docker lên AWS (EC2 + RDS + S3).

---

## 📋 Mục Lục

1. [AWS Resources Information](#-aws-resources-information)
2. [PHASE 1: Database Migration](#-phase-1-database-migration--data-patching)
3. [PHASE 2: EC2 Deployment](#-phase-2-ec2-deployment)
4. [PHASE 3: Verification](#-phase-3-verification)
5. [Useful Commands](#-useful-commands)
6. [Quick Start](#-quick-start)

---

## 📋 AWS Resources Information

| Resource | Value |
|----------|-------|
| **RDS Endpoint** | `travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com` |
| **RDS Port** | `5434` |
| **RDS User** | `postgres` |
| **RDS Database** | `travel_db` |
| **S3 Bucket** | `travel-img-drive` |
| **S3 URL Base** | `https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/` |

---

## 🟢 PHASE 1: Database Migration & Data Patching

### Step 1.0: Cài đặt và cấu hình psql (PostgreSQL Client)

> ⚠️ **Yêu cầu**: Phải cài PostgreSQL client để chạy các lệnh import database.

#### Windows

1. **Download PostgreSQL** từ: https://www.postgresql.org/download/windows/

2. **Cài đặt** (chỉ cần chọn "Command Line Tools" nếu không cần database local)

3. **Thêm vào PATH** (chạy trong PowerShell):
```powershell
# Thêm PostgreSQL bin vào PATH (phiên hiện tại)
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"

# Hoặc thêm vĩnh viễn vào System Environment Variables thủ công:
# Settings > System > About > Advanced system settings > Environment Variables > Path > Add new
```

4. **Kiểm tra cài đặt**:
```powershell
where psql
psql --version
```

#### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt install postgresql-client -y

# macOS (Homebrew)
brew install libpq && brew link --force libpq
```

---

### Step 1.1: Reset Database (Nếu đã có dữ liệu)

> ⚠️ **CHÚ Ý**: Nếu bạn đã import dữ liệu trước đó và muốn ghi đè, cần DROP database cũ trước.

**Cách 1: Drop và tạo lại database (khuyến nghị)**

```powershell
$env:PGPASSWORD="<YOUR_RDS_PASSWORD>"

# Bước 1: Force terminate tất cả sessions đang kết nối đến travel_db
# (Không ảnh hưởng nếu không ai đang dùng production)
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d postgres `
     -p 5434 `
     -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'travel_db' AND pid <> pg_backend_pid();"

# Bước 2: Drop và tạo lại database
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d postgres `
     -p 5434 `
     -c "DROP DATABASE IF EXISTS travel_db; CREATE DATABASE travel_db;"
```

> 💡 **Lưu ý**: Lệnh `pg_terminate_backend` sẽ ngắt kết nối của các sessions khác đang dùng database. Chỉ chạy khi chắc chắn không có ai đang làm việc với production.

**Cách 2: Xóa dữ liệu và import lại (giữ cấu trúc bảng)**

```powershell
# Bước 1: Tắt kiểm tra foreign key, truncate tất cả bảng, bật lại
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -c "SET session_replication_role = replica; TRUNCATE TABLE visit_logs, user_post_favorites, user_place_favorites, tourist_attractions, restaurants, hotels, place_images, places, token_refresh, activity_logs, users, roles, place_types, districts RESTART IDENTITY CASCADE; SET session_replication_role = DEFAULT;"

# Bước 2: Tắt kiểm tra foreign key trước khi import
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -c "SET session_replication_role = replica;" `
     -f "d:\CSDL_Web\WEB_Final\src\database\init.sql"
```

> ⚠️ **Lỗi thường gặp**:
> - `database is being accessed by other users` → Dùng Cách 1 với lệnh terminate sessions
> - `violates foreign key constraint` → Dùng `SET session_replication_role = replica` để tạm tắt foreign key checks

---

### Step 1.2: Import Data to RDS

Chạy lệnh sau từ máy local:

**Windows PowerShell:**
```powershell
$env:PGPASSWORD="<YOUR_RDS_PASSWORD>"

psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -f "d:\CSDL_Web\WEB_Final\src\database\init.sql"
```

**Linux/Mac:**
```bash
export PGPASSWORD="<YOUR_RDS_PASSWORD>"

psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com \
     -U postgres \
     -d travel_db \
     -p 5434 \
     -f "./src/database/init.sql"
```

---

### Step 1.3: Patch Image Paths for S3

Sau khi import xong, chạy script patch để cập nhật đường dẫn ảnh:

```powershell
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -f "d:\CSDL_Web\WEB_Final\src\database\patch_data.sql"
```

---

### Step 1.4: Verify Data

```powershell
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -c "SELECT image_url FROM place_images LIMIT 5;"
```

✅ **Expected**: URLs bắt đầu với `https://travel-img-drive.s3.ap-southeast-1.amazonaws.com/uploads/`

---

## 🔵 PHASE 2: EC2 Deployment

### 2.1 Yêu cầu chuẩn bị

#### Thông tin EC2 Instance
- **OS**: Ubuntu (t2.small hoặc tương đương)
- **PEM Key**: `travel-web-server.pem`
- **Security Group**: Mở port 22 (SSH), 80 (HTTP), 8000 (Backend)

#### Files cần chuẩn bị trên máy local
- `travel-web-server.pem` - SSH key
- `src/.env.prod` - File môi trường production

---

### 2.2 Kết nối SSH đến EC2

#### Chuẩn bị PEM Key

**Windows (PowerShell):**
```powershell
cd D:\CSDL_Web\WEB_Final
dir travel-web-server.pem
```

**Linux/Mac:**
```bash
chmod 400 travel-web-server.pem
```

#### Kết nối SSH

Thay `<EC2_PUBLIC_IP>` bằng IP thực của EC2:

```powershell
ssh -i "travel-web-server.pem" ubuntu@<EC2_PUBLIC_IP>
```

**Ví dụ:**
```bash
ssh -i "travel-web-server.pem" ubuntu@13.214.31.54
```

#### Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|-----|-------------|----------------|
| `Permission denied (publickey)` | Sai user hoặc key | Đảm bảo dùng user `ubuntu` và đúng PEM file |
| `Connection timed out` | Port 22 bị chặn | Kiểm tra Security Group, mở port 22 |
| `Permissions are too open` | Quyền PEM cao quá | Chạy `chmod 400 travel-web-server.pem` |

---

### 2.3 Cài đặt môi trường trên EC2

**Sau khi SSH thành công, chạy các lệnh sau trên EC2:**

#### Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```

#### Cài đặt Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

#### Cài đặt Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

#### Cài đặt Git
```bash
sudo apt install git -y
git --version
```

#### Cài đặt Ngrok
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Cấu hình authtoken
ngrok config add-authtoken 31kCrraaQxYR445857rgbRfDszz_2UHQ7GWh5vHFudAKQri1n
ngrok version
```

---

### 2.4 Clone và Build ứng dụng

#### Clone repository và checkout branch
```bash
cd ~
git clone https://github.com/<YOUR_USERNAME>/WEB_Final.git
cd WEB_Final

# ⚠️ QUAN TRỌNG: Chuyển sang branch cloud-migration
git checkout cloud-migration
git pull origin cloud-migration

cd src
```

#### Kiểm tra cấu trúc
```bash
ls -la
# Phải thấy: docker-compose.prod.yml, frontend/, backend/
```

---

### 2.5 Upload file môi trường (.env)

> ⚠️ **QUAN TRỌNG**: File `.env.prod` chứa thông tin nhạy cảm và KHÔNG được commit lên Git. Phải upload thủ công qua SCP.

#### Upload từ máy local lên EC2

**Mở terminal MỚI trên máy local (không phải SSH session):**

**Windows (PowerShell):**
```powershell
cd D:\CSDL_Web\WEB_Final
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@<EC2_PUBLIC_IP>:~/WEB_Final/src/.env.prod
```

**Ví dụ:**
```powershell
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@13.214.31.54:~/WEB_Final/src/.env.prod
```

#### Verify file đã upload (trên EC2)

Quay lại SSH session và kiểm tra:
```bash
cd ~/WEB_Final/src
cat .env.prod | head -20
```

---

### 2.6 Build và chạy Docker

```bash
# Build images
docker-compose -f docker-compose.prod.yml --env-file .env.prod build

# Chạy containers
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Kiểm tra trạng thái
docker ps
```

**Kết quả mong đợi:**
```
NAMES                  STATUS         PORTS
travel_frontend_prod   Up (healthy)   0.0.0.0:80->80/tcp
travel_backend_prod    Up (healthy)   0.0.0.0:8000->8000/tcp
```

---

### 2.7 Cấu hình Ngrok (Optional - cho Public URL)

```bash
# Cài screen
sudo apt install screen -y

# Tạo session mới
screen -S ngrok

# Chạy ngrok
ngrok http 80

# Nhấn Ctrl+A rồi D để detach (ngrok vẫn chạy)
# Để quay lại: screen -r ngrok
```

Ngrok sẽ hiển thị URL như:
```
Forwarding    https://xxxx-xx-xx-xx.ngrok-free.app -> http://localhost:80
```

---

## ✅ PHASE 3: Verification

### Kiểm tra Containers
```bash
docker ps
docker logs travel_backend_prod --tail 20
```

### Kiểm tra Endpoints
```bash
curl http://localhost:8000/health
curl -I http://localhost
```

### Browser Test
Mở browser: `http://<EC2_PUBLIC_IP>` hoặc URL ngrok

### Xem logs real-time
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 Useful Commands

```bash
# SSH vào EC2
ssh -i "travel-web-server.pem" ubuntu@<EC2_IP>

# Upload .env file từ local
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@<EC2_IP>:~/WEB_Final/src/.env.prod

# Kiểm tra Docker containers
docker ps

# Xem logs
docker logs travel_backend_prod -f

# Restart containers
docker-compose -f docker-compose.prod.yml --env-file .env.prod restart

# Stop tất cả
docker-compose -f docker-compose.prod.yml down

# Rebuild và chạy lại
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Enter container shell
docker exec -it travel_backend_prod /bin/bash

# Ngrok session
screen -r ngrok
```

---

## 🚀 Quick Start

```bash
# 1. SSH vào EC2
ssh -i "travel-web-server.pem" ubuntu@13.214.31.54

# 2. Clone và checkout đúng branch
git clone https://github.com/<YOUR_USERNAME>/WEB_Final.git
cd WEB_Final
git checkout cloud-migration
cd src

# 3. (Mở terminal khác) Upload .env từ local
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@13.214.31.54:~/WEB_Final/src/.env.prod

# 4. Build và run Docker
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# 5. Chạy Ngrok (optional)
screen -S ngrok
ngrok http 80
# Ctrl+A, D để detach
```

---

## 📁 Files Created

| File | Description |
|------|-------------|
| `src/database/patch_data.sql` | SQL script cập nhật đường dẫn ảnh sang S3 |
| `src/frontend/Dockerfile` | Production Dockerfile cho Frontend (Nginx) |
| `src/backend/Dockerfile.prod` | Production Dockerfile cho Backend (Gunicorn) |
| `src/docker-compose.prod.yml` | Docker Compose cho production |
| `src/.env.prod` | File biến môi trường production |
