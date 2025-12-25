FROM python:3.9-slim

WORKDIR /app

# 1. Copy requirements từ thư mục con ra root của container để cài đặt
# Lưu ý đường dẫn nguồn: tests/database/requirements.txt
COPY tests/database/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy file main.py từ thư mục con ra root của container
COPY tests/database/main.py .

# 3. Tạo thư mục static để hứng volume ảnh
RUN mkdir -p /app/static/uploads

# 4. Chạy server (lúc này main.py đã nằm ngay tại /app nên gọi bình thường)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]