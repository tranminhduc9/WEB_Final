# Hướng Dẫn Deploy Hanoi Travel lên AWS EC2

## Mục Lục
1. [Yêu cầu chuẩn bị](#1-yêu-cầu-chuẩn-bị)
2. [Kết nối SSH đến EC2](#2-kết-nối-ssh-đến-ec2)
3. [Cài đặt môi trường trên EC2](#3-cài-đặt-môi-trường-trên-ec2)
4. [Clone và Build ứng dụng](#4-clone-và-build-ứng-dụng)
5. [Upload file môi trường (.env)](#5-upload-file-môi-trường-env)
6. [Cấu hình Ngrok](#6-cấu-hình-ngrok)
7. [Kiểm tra và Xác nhận](#7-kiểm-tra-và-xác-nhận)

---

## 1. Yêu cầu chuẩn bị

### Thông tin EC2 Instance
- **OS**: Ubuntu (t2.small hoặc tương đương)
- **PEM Key**: `travel-web-server.pem`
- **Security Group**: Mở port 22 (SSH), 80 (HTTP), 8000 (Backend)

### Thông tin AWS Services
| Service | Endpoint |
|---------|----------|
| RDS | `travel-db-server.c524kcki6eag.ap-southeast-1.rds.amazonaws.com:5434` |
| S3 | `travel-img-drive.s3.ap-southeast-1.amazonaws.com` |

### Files cần chuẩn bị trên máy local
- `travel-web-server.pem` - SSH key
- `src/.env.prod` - File môi trường production

---

## 2. Kết nối SSH đến EC2

### Bước 2.1: Chuẩn bị PEM Key

**Windows (PowerShell):**
```powershell
# Di chuyển đến thư mục chứa PEM file
cd D:\CSDL_Web\WEB_Final

# Kiểm tra file tồn tại
dir travel-web-server.pem
```

**Linux/Mac:**
```bash
# Set quyền cho PEM file (bắt buộc)
chmod 400 travel-web-server.pem
```

### Bước 2.2: Kết nối SSH

Thay `<EC2_PUBLIC_IP>` bằng IP thực của EC2 (ví dụ: `13.214.31.54`):

**Windows (PowerShell hoặc CMD):**
```powershell
ssh -i "travel-web-server.pem" ubuntu@<EC2_PUBLIC_IP>
```

**Ví dụ:**
```bash
ssh -i "travel-web-server.pem" ubuntu@13.214.31.54
```

### Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|-----|-------------|----------------|
| `Permission denied (publickey)` | Sai user hoặc key | Đảm bảo dùng user `ubuntu` và đúng PEM file |
| `Connection timed out` | Port 22 bị chặn | Kiểm tra Security Group, mở port 22 |
| `Permissions are too open` | Quyền PEM cao quá | Chạy `chmod 400 travel-web-server.pem` |

---

## 3. Cài đặt môi trường trên EC2

**Sau khi SSH thành công, chạy các lệnh sau trên EC2:**

### Bước 3.1: Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```

### Bước 3.2: Cài đặt Docker
```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Thêm user vào docker group
sudo usermod -aG docker $USER

# Áp dụng thay đổi group
newgrp docker

# Kiểm tra
docker --version
```

### Bước 3.3: Cài đặt Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Kiểm tra
docker-compose --version
```

### Bước 3.4: Cài đặt Git
```bash
sudo apt install git -y
git --version
```

### Bước 3.5: Cài đặt Ngrok
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok -y

# Cấu hình authtoken
ngrok config add-authtoken 31kCrraaQxYR445857rgbRfDszz_2UHQ7GWh5vHFudAKQri1n

# Kiểm tra
ngrok version
```

---

## 4. Clone và Build ứng dụng

### Bước 4.1: Clone repository và checkout branch
```bash
cd ~
git clone https://github.com/<YOUR_USERNAME>/WEB_Final.git
cd WEB_Final

# ⚠️ QUAN TRỌNG: Chuyển sang branch cloud-migration
git checkout cloud-migration
git pull origin cloud-migration

# Vào thư mục source
cd src
```

### Bước 4.2: Kiểm tra cấu trúc
```bash
ls -la
# Phải thấy: docker-compose.prod.yml, frontend/, backend/
```

---

## 5. Upload file môi trường (.env)

> ⚠️ **QUAN TRỌNG**: File `.env.prod` chứa thông tin nhạy cảm và KHÔNG được commit lên Git. Phải upload thủ công qua SCP.

### Bước 5.1: Upload từ máy local lên EC2

**Mở terminal MỚI trên máy local (không phải SSH session):**

**Windows (PowerShell):**
```powershell
# Di chuyển đến thư mục project
cd D:\CSDL_Web\WEB_Final

# Upload file .env.prod lên EC2
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@<EC2_PUBLIC_IP>:~/WEB_Final/src/.env.prod
```

**Ví dụ:**
```powershell
scp -i "travel-web-server.pem" "src/.env.prod" ubuntu@13.214.31.54:~/WEB_Final/src/.env.prod
```

**Linux/Mac:**
```bash
scp -i "travel-web-server.pem" src/.env.prod ubuntu@<EC2_PUBLIC_IP>:~/WEB_Final/src/.env.prod
```

### Bước 5.2: Verify file đã upload (trên EC2)

Quay lại SSH session và kiểm tra:
```bash
cd ~/WEB_Final/src
cat .env.prod | head -20
```

### Bước 5.3: Build và chạy Docker
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

## 6. Cấu hình Ngrok

### Bước 6.1: Chạy Ngrok với screen (khuyến nghị)
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

### Kết quả
Ngrok sẽ hiển thị URL như:
```
Forwarding    https://xxxx-xx-xx-xx.ngrok-free.app -> http://localhost:80
```

Chia sẻ URL này cho người khác truy cập web!

---

## 7. Kiểm tra và Xác nhận

### Kiểm tra containers
```bash
docker ps
docker logs travel_backend_prod --tail 20
```

### Kiểm tra endpoints
```bash
curl http://localhost:8000/health
curl -I http://localhost
```

### Xem logs real-time
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Tóm tắt các lệnh quan trọng

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

# Ngrok session
screen -r ngrok
```

---

## Quick Start (Tóm tắt nhanh)

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

# 5. Chạy Ngrok
screen -S ngrok
ngrok http 80
# Ctrl+A, D để detach
```
