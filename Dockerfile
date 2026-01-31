FROM python:3.9-slim

# Logların anlık akması için (AWS loglarında bekleme yapmaz)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Gereksinimleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm dosyaları kopyala
COPY . .

# ---------------------------------------------------------
# ÇÖZÜM BURASI: DB Klasörünü manuel olarak oluşturuyoruz
# .dockerignore engellese bile bu komut klasörü yaratır.
# ---------------------------------------------------------
RUN mkdir -p /app/db

# Portları aç
EXPOSE 8000
EXPOSE 8501

# Uygulamayı başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
