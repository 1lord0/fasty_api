FROM python:3.9-slim

WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# Portları aç
EXPOSE 8000
EXPOSE 8501

# Streamlit ve FastAPI'yi tek satırda başlat (Dosya hatasını bypass ediyoruz)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]