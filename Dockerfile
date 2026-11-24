# 1. Yengil va xavfsiz rasmiy Python 3.11 bazaviy obrazi
FROM python:3.11-slim


# 2. Python muhit o'zgaruvchilari (Kesh yozmaslik va loglarni tezkor chiqarish)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 3. Konteyner ichidagi asosiy ishchi papka
WORKDIR /app

# 4. Tizim darajasidagi PostgreSQL drayveri va kerakli utilitalarni o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Yuqori tezlikdagi uv paket menejerini ko'chirib olish
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv


# 6. Bog'liqlik fayllarini nusxalash (Keshlanishni optimallashtirish uchun)
COPY pyproject.toml uv.lock ./

# 7. Paketlarni tizim muhitiga to'liq o'rnatish (gunicorn va whitenoise bilan birga)
RUN uv pip install --system --no-cache -r pyproject.toml gunicorn whitenoise

# 8. Loyihaning barcha fayllarini konteynerga nusxalash
COPY . .

# 9. Statik va Media fayllar uchun papkalar yaratish
RUN mkdir -p /app/staticfiles /app/media

# 10. Web portni ochish
EXPOSE 8000


# 11. Standart ishga tushirish buyrug'i (3 ta ishchi oqim bilan Gunicorn)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]