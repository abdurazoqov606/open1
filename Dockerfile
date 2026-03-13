# Asosiy Python tizimi
FROM python:3.10-slim

# Linux uchun kerakli kutubxonalar va brauzerni o'rnatish
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    wget \
    gnupg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Ishchi papkani yaratish
WORKDIR /app

# Kutubxonalar ro'yxatini ko'chirish
COPY requirements.txt .

# pip'ni yangilash va kutubxonalarni o'rnatish (XATONI OLDINI OLISH UCHUN)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Asosiy kodni ko'chirish
COPY bot.py .

# Botni ishga tushirish buyrug'i
CMD ["python", "bot.py"]
