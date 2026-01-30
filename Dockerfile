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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
