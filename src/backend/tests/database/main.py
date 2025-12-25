from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
import os

app = FastAPI()

# Mount folder ảnh: /static/uploads (ảo) -> /app/static/uploads (thật trong container)
app.mount("/static/uploads", StaticFiles(directory="/app/static/uploads"), name="static")

# Kết nối DB từ biến môi trường
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.get("/")
def read_root():
    return {"message": "Hanoi Travel Test Backend is Running form tests/database!"}

@app.get("/test-places")
def get_test_places():
    # Query 5 địa điểm bất kỳ có ảnh
    query = text("""
        SELECT p.id, p.name, pi.image_url 
        FROM places p 
        JOIN place_images pi ON p.id = pi.place_id 
        WHERE pi.is_main = true 
        LIMIT 5
    """)
    with engine.connect() as conn:
        result = conn.execute(query).fetchall()
        
    data = []
    for row in result:
        # row[2] là đường dẫn trong DB: /static/uploads/...
        full_url = f"http://localhost:8000{row[2]}"
        data.append({
            "id": row[0],
            "name": row[1],
            "db_path": row[2],
            "test_link": full_url
        })
    return data