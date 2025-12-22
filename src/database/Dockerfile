# Sử dụng PostgreSQL 17 - phiên bản ổn định mới nhất
FROM postgres:17-alpine

# Metadata
LABEL maintainer="devops-team@travel.com"
LABEL description="PostgreSQL 17 with auto-init from SQL file"
LABEL version="1.0"

# Set timezone (optional - tùy chọn múi giờ)
ENV TZ=Asia/Ho_Chi_Minh

# Copy file init.sql vào thư mục khởi tạo tự động
# PostgreSQL sẽ tự động chạy các file .sql trong thư mục này khi container khởi tạo lần đầu
COPY init.sql /docker-entrypoint-initdb.d/

# Set quyền cho file (đảm bảo có thể đọc được)
RUN chmod 644 /docker-entrypoint-initdb.d/init.sql

# Expose port 5432 (documentation purpose)
EXPOSE 5432

# Health check built-in sẽ được định nghĩa trong docker-compose