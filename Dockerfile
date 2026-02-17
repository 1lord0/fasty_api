# Python 3.11-slim kullanarak biraz daha güncel ve hafif bir temel atıyoruz
FROM python:3.11-slim

# Sistem bağımlılıklarını ve temizliği tek adımda yapıp imajı küçültüyoruz
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Gereksinimleri kopyala ve cache kullanmadan yükle (Disk tasarrufu için)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# DB klasörünü oluştur ve izinleri ayarla
RUN mkdir -p /app/db && chmod 777 /app/db

# Portları aç
EXPOSE 8000
EXPOSE 8501

# ---------------------------------------------------------
# ÇÖZÜM: Hem FastAPI hem Streamlit'i aynı anda başlatmak için
# 'bash' kullanarak iki komutu birden çalıştırıyoruz.
# ---------------------------------------------------------
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.baseUrlPath /dashboard"
