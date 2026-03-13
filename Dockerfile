# Asosiy Python tizimi
FROM python:3.10-slim

# Linux uchun kerakli kutubxonalar va Chromium brauzerini o'rnatish
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Ishchi papkani yaratish
WORKDIR /app

# Kutubxonalar ro'yxatini ko'chirish va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Asosiy kodni ko'chirish
COPY bot.py .

# Botni ishga tushirish buyrug'i
CMD ["python", "bot.py"]
