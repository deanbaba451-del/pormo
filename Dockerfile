# Hafif ve güncel bir Python sürümü seçiyoruz
FROM python:3.10-slim

# Çalışma dizinini oluştur
WORKDIR /app

# Sistem bağımlılıklarını güncelle
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Önce gereksinimleri kopyala ve kur (Cache avantajı sağlar)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Render'ın beklediği varsayılan port
EXPOSE 8080

# Botu ve Flask'ı beraber çalıştıran ana dosyayı başlat
CMD ["python", "z.py"]
