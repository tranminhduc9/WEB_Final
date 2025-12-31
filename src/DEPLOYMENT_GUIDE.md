# 🚀 AWS Deployment Guide - Travel Web Application

Hướng dẫn triển khai ứng dụng từ Local Docker lên AWS (EC2 + RDS + S3).

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

### Step 1.1: Import Data to RDS

Chạy lệnh sau từ máy local (đảm bảo đã cài `psql`):

```powershell
# Windows PowerShell
$env:PGPASSWORD="<YOUR_RDS_PASSWORD>"

psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -f "d:\CSDL_Web\WEB_Final\src\database\init.sql"
```

```bash
# Linux/Mac
export PGPASSWORD="<YOUR_RDS_PASSWORD>"

psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com \
     -U postgres \
     -d travel_db \
     -p 5434 \
     -f "./src/database/init.sql"
```

### Step 1.2: Patch Image Paths for S3

Sau khi import xong, chạy script patch để cập nhật đường dẫn ảnh:

```powershell
# Windows
psql -h travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com `
     -U postgres `
     -d travel_db `
     -p 5434 `
     -f "d:\CSDL_Web\WEB_Final\src\database\patch_data.sql"
```

### Step 1.3: Verify Data

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

### Step 2.1: SSH to EC2

```bash
ssh -i "travel-web-server.pem" ubuntu@<EC2_PUBLIC_IP>
```

### Step 2.2: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Step 2.3: Clone Repository

```bash
cd ~
git clone <YOUR_REPO_URL> travel-app
cd travel-app/src
```

### Step 2.4: Setup Environment

```bash
# Copy production env template
cp .env.production .env

# Edit with your values
nano .env
```

**Thay đổi các giá trị sau trong `.env`:**
- `<RDS_PASSWORD>` - Password RDS của bạn
- `<CHANGE_THIS_GENERATE_NEW_KEY>` - Tạo key mới bằng: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- `<EC2_PUBLIC_IP>` - IP public của EC2
- `<YOUR_DOMAIN>` - Domain của bạn (nếu có)

### Step 2.5: Build & Start

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 2.6: Configure Firewall

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow Backend API (optional - nếu cần truy cập trực tiếp)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

---

## ✅ Verification

### Check Containers

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                    STATUS                    PORTS
xxxxx          src-frontend             Up (healthy)              0.0.0.0:80->80/tcp
xxxxx          src-backend              Up (healthy)              0.0.0.0:8000->8000/tcp
```

### Test Endpoints

```bash
# Frontend
curl -I http://localhost

# Backend Health
curl http://localhost:8000/api/v1/health

# Swagger Docs
curl http://localhost:8000/docs
```

### Browser Test

Mở browser: `http://<EC2_PUBLIC_IP>`

---

## 🔧 Useful Commands

```bash
# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop all
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# View specific logs
docker logs travel_backend_prod -f
docker logs travel_frontend_prod -f

# Enter container shell
docker exec -it travel_backend_prod /bin/bash
```

---

## 📁 Files Created

| File | Description |
|------|-------------|
| `src/database/patch_data.sql` | SQL script cập nhật đường dẫn ảnh sang S3 |
| `src/frontend/Dockerfile` | Production Dockerfile cho Frontend (Nginx) |
| `src/backend/Dockerfile.prod` | Production Dockerfile cho Backend (Gunicorn) |
| `src/docker-compose.prod.yml` | Docker Compose cho production |
| `src/.env.production` | Template biến môi trường production |
