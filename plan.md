# 🚀 10-BOSQICH (PHASE 10): EVENTLY LOYIHASI UCHUN TO'LIQ DEPLOYMENT VA AWS QO'LLANMASI

> **Loyiha auditi xulosasi:**  
> Ushbu qo'llanma sizning joriy **Evently** loyihangizning barcha arxitekturaviy xususiyatlariga (Django 5.2, `uv` paket menejeri, PostgreSQL/psycopg, Jazzmin Admin, DRF Spectacular (`/api/docs/`), Aiogram 3 Telegram Bot va `send_event_reminders` management command) **100% moslashtirilgan holda** tayyorlandi.

---

## 📋 MUNDARIJA
1. [1-QADAM: Loyihaning joriy holati va Production sozlamalari](#1-qadam-loyihaning-joriy-holati-va-production-sozlamalari)
2. [2-QADAM: AWS EC2 Serverini sozlash (Inbound Rules va Elastic IP)](#2-qadam-aws-ec2-serverini-sozlash-inbound-rules-va-elastic-ip)
3. [3-QADAM: Evently Botni AWS da to'g'ri ulash va 24/7 ishlatish](#3-qadam-evently-botni-aws-da-togri-ulash-va-247-ishlatish)
4. [4-QADAM: 1-USUL: Docker & Docker Compose orqali deploy (Eng qulay va tavsiya etilgan)](#4-qadam-1-usul-docker--docker-compose-orqali-deploy-eng-qulay-va-tavsiya-etilgan)
5. [5-QADAM: 2-USUL: VPS (Ubuntu) da Systemd + Nginx + SSL orqali to'g'ridan-to'g'ri deploy](#5-qadam-2-usul-vps-ubuntu-da-systemd--nginx--ssl-orqali-togridan-togri-deploy)
6. [6-QADAM: Tadbirlar Eslatmasini (Reminders) Cron orqali avtomatlashtirish](#6-qadam-tadbirlar-eslatmasini-reminders-cron-orqali-avtomatlashtirish)
7. [7-QADAM: Muqobil variant: Render.com orqali tezkor deploy](#7-qadam-muqobil-variant-rendercom-orqali-tezkor-deploy)
8. [8-QADAM: Evently loyihasini tekshirish nazorat ro'yxati (Deployment Checklist)](#8-qadam-evently-loyihasini-tekshirish-nazorat-royxati-deployment-checklist)

---

## 🛠 1-QADAM: Loyihaning joriy holati va Production sozlamalari

### 1.1. Kerakli paketlarni o'rnatish
Hozirda `pyproject.toml` da production serveri (`gunicorn`) va statik fayllar uchun (`whitenoise`) yo'q. Ularni qo'shing:

```bash
uv add gunicorn whitenoise
```
*Agar serverda `requirements.txt` kerak bo'lsa:*
```bash
uv pip compile pyproject.toml -o requirements.txt
```

---

### 1.2. `config/settings.py` fayliga kerakli qo'shimchalar

Productionda xatoliklarsiz ishlashi uchun `config/settings.py` ga quyidagi sozlamalarni kiriting:

#### A) WhiteNoise Middleware (Jazzmin va Admin statikalari buzilmasligi uchun):
`MIDDLEWARE` ro'yxatida `SecurityMiddleware` dan keyin darhol `whitenoise.middleware.WhiteNoiseMiddleware` bo'lishi shart:
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- SHU YERGA QO'SHILADI
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

#### B) Statik va Media fayllar:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### C) Host, CSRF va CORS xavfsizligi:
```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", 
    default=["http://localhost:8000", "http://127.0.0.1"]
)

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://localhost:5173"]
)

# Nginx yoki SSL orqasida to'g'ri ishlashi uchun:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## 🌐 2-QADAM: AWS EC2 Serverini sozlash (Inbound Rules va Elastic IP)

### 2.1. AWS EC2 instansiya ochish
1. **AWS Management Console** -> **EC2** -> **Launch Instance**.
2. **Nom**: `evently-prod-server`.
3. **OS**: **Ubuntu Server 24.04 LTS** (64-bit x86).
4. **Instance Type**: `t2.micro` yoki `t3.micro` (AWS Free Tier).
5. **Key pair**: Yangi `.pem` kalit yarating va kompyuteringizga yuklab oling (masalan, `evently-key.pem`).

### 2.2. Xavfsizlik guruhini sozlash (Security Group Inbound Rules)
AWS konsolida quyidagi tarmoq portlarini oching:
- **SSH (Port 22)**: Sizning shaxsiy IP manzilingiz (`My IP`) yoki barcha uchun (`0.0.0.0/0`).
- **HTTP (Port 80)**: `Anywhere (0.0.0.0/0)` (Web so'rovlar uchun).
- **HTTPS (Port 443)**: `Anywhere (0.0.0.0/0)` (Shifrlangan SSL ulanish uchun).
- ⚠️ **PostgreSQL (Port 5432)**: **TASHQARIGA OCHMANG!** Baza faqat server ichida (`localhost` yoki Docker tarmog'i) himoyalangan holda ishlashi kerak.

### 2.3. Elastic IP (Doimiy statik IP olish)
1. EC2 Menyusi -> **Elastic IPs** -> **Allocate Elastic IP address**.
2. Olingan IP manzilni **Actions** -> **Associate Elastic IP address** orqali `evently-prod-server` instansiyasiga ulang.

### 2.4. Serverga SSH orqali ulanish
Terminal orqali `.pem` fayli joylashgan papkaga o'ting:
```bash
# Fayl huquqini to'g'rilash:
chmod 400 evently-key.pem

# Serverga ulanish:
ssh -i "evently-key.pem" ubuntu@<SIZNING_ELASTIC_IP>
```

---

## 🤖 3-QADAM: Evently Botni AWS da to'g'ri ulash va 24/7 ishlatish

### 3.1. Bot va Backend integratsiyasi qanday ishlaydi?
Loyihangizda Telegram bot va Django o'rtasidagi aloqa quyidagicha tashkil etilgan:
1. **Foydalanuvchini ulash**: Saytdan yoki botdan `/start <token>` yuborilganda, bot `bot/api_client.py` orqali Django API dagi `/api/v1/notifications/telegram/confirm/` endpointiga `POST` so'rov jo'natadi.
2. **Himoya (Secret Key)**: Bot so'rov jo'natishda sarlavhaga `X-Bot-Secret: BOT_API_SECRET` ni biriktiradi. Django esa faqat shu maxfiy paroli bor so'rovlarni qabul qiladi.
3. **Mening tadbirlarim**: Foydalanuvchi botda `/my_events` buyrug'ini yozganda, bot `/api/v1/notifications/telegram/my-events/` dan chiptalarni olib ko'rsatadi.
4. **Bildirishnomalar**: Foydalanuvchi tadbirga ro'yxatdan o'tganda yoki eslatma yuborilganda, Django to'g'ridan-to'g'ri Telegram API ga xabar yuboradi.

### 3.2. Bot uchun `.env` dagi muhim parametrlar
AWS serverdagi `.env` faylida ushbu 4 ta qiymat aniq ko'rsatilishi shart:

```env
# 1. Telegram Bot Tokeni
TELEGRAM_BOT_TOKEN=9230877104:AAEMtZJuZcuVL1rYM1wAKdrgQQfyWDwSuRo

# 2. Telegram Bot Username
TELEGRAM_BOT_USERNAME=myeventlyBot

# 3. Backend va Bot o'rtasidagi maxfiy kalit (ikkala tomonda ham bir xil bo'lishi shart!)
BOT_API_SECRET=WNYUTp-YkgvHGELCTVlq2BjioJ3mPwkr8mBs4Cb7h7s

# 4. Backend API ning bazaviy URL manzili:
# - Agar Docker ishlatilsa:
BACKEND_API_URL=http://web:8000/api/v1
# - Agar Systemd (Ubuntu native) ishlatilsa:
# BACKEND_API_URL=http://127.0.0.1:8000/api/v1
```

### 3.3. Botning uzluksiz ishlashi (Auto-Restart)
Bot terminal yopilganda o'chib qolmasligi va agar Telegram API yoki internetda uzilish bo'lsa ham avtomatik qayta yonishi uchun:
- Docker'da: `restart: always` parametri qo'llaniladi.
- Systemd'da: `Restart=always` va `RestartSec=5` ko'rsatiladi.

---

## 🐳 4-QADAM: 1-USUL: Docker & Docker Compose orqali deploy (Tavsiya etiladi)

Bu usul AWS serverda barcha xizmatlarni (PostgreSQL, Django Gunicorn, Aiogram Bot) bitta buyruq bilan mustaqil konteynerlarda ko'taradi.

### 4.1. Serverga Docker o'rnatish
Serverga ulangach, buyruqlarni bajaring:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu
newgrp docker
```

### 4.2. Loyihani yuklab olish
```bash
cd /home/ubuntu
git clone https://github.com/<sizning-github>/Project-evently.git
cd Project-evently/evently
```

### 4.3. Loyiha fayllari

#### A) `Dockerfile` (Loyiha ildizida):
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache -r pyproject.toml gunicorn whitenoise

COPY . .

RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

#### B) `.dockerignore`:
```text
.venv/
__pycache__/
*.pyc
.git/
.env
.pytest_cache/
tests/
Dockerfile
docker-compose.yml
plan.md
postman/
```

#### C) `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: evently_postgres
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME:-evently_db}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-strong_secret_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - evently_network

  web:
    build: .
    container_name: evently_web
    restart: always
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DEBUG=False
    depends_on:
      - db
    networks:
      - evently_network

  bot:
    build: .
    container_name: evently_bot
    restart: always
    command: python -m bot.main
    env_file:
      - .env
    environment:
      - BACKEND_API_URL=http://web:8000/api/v1
    depends_on:
      - web
    networks:
      - evently_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  evently_network:
    driver: bridge
```

### 4.4. Serverda `.env` faylini yaratish
`nano .env` buyrug'i bilan quyidagi tarkibni saqlang:

```env
# Django Sozlamalari
DEBUG=False
SECRET_KEY=xqzr6m-=8wpk-=khsy8m&)0ano1!_@w4#%tszydwk44lw+2g&3-aws-prod-key
ALLOWED_HOSTS=<SIZNING_ELASTIC_IP>,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://<SIZNING_ELASTIC_IP>,http://localhost:8000
TIME_ZONE=Asia/Tashkent

# Database Sozlamalari
DB_NAME=evently_db
DB_USER=postgres
DB_PASSWORD=strong_postgres_password_2026!
DB_HOST=db
DB_PORT=5432

# JWT Sozlamalari
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Telegram Bot Sozlamalari
TELEGRAM_BOT_TOKEN=9230877104:AAEMtZJuZcuVL1rYM1wAKdrgQQfyWDwSuRo
TELEGRAM_BOT_USERNAME=myeventlyBot
BOT_API_SECRET=WNYUTp-YkgvHGELCTVlq2BjioJ3mPwkr8mBs4Cb7h7s
BACKEND_API_URL=http://web:8000/api/v1

# Reminders
REMINDER_HOURS_BEFORE=24
```

### 4.5. Ishga tushirish va Boshqaruv buyruqlari
```bash
# 1. Konteynerlarni qurish va orqa fonda ishga tushirish:
docker compose up -d --build

# 2. Superuser (admin) yaratish:
docker compose exec web python manage.py createsuperuser

# 3. Telegram bot loglarini ko'rish (Jonli):
docker compose logs -f bot
# Terminalda: "Evently Telegram Bot ishga tushmoqda..." chiqishi kerak.

# 4. Web server loglarini ko'rish:
docker compose logs -f web

# 5. Konteynerlarni to'xtatish:
docker compose down
```

---

## ⚡ 5-QADAM: 2-USUL: VPS (Ubuntu) da Systemd + Nginx + SSL orqali to'g'ridan-to'g'ri deploy

Agar Docker siz to'g'ridan-to'g'ri Ubuntu server tizimida ishlatmoqchi bo'lsangiz:

### 5.1. PostgreSQL o'rnatish
```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE DATABASE evently_db;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'strong_password_123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE evently_db TO postgres;"
sudo -u postgres psql -c "ALTER DATABASE evently_db OWNER TO postgres;"
```

### 5.2. Muhitni sozlash va paketlarni o'rnatish
```bash
cd /home/ubuntu/Project-evently/evently
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt gunicorn whitenoise
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 5.3. Django Web uchun Systemd xizmati
Fayl yarating: `sudo nano /etc/systemd/system/evently-web.service`

```ini
[Unit]
Description=Gunicorn daemon for Evently Django
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Project-evently/evently
EnvironmentFile=/home/ubuntu/Project-evently/evently/.env
ExecStart=/home/ubuntu/Project-evently/evently/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.4. Telegram Bot uchun Systemd xizmati
Fayl yarating: `sudo nano /etc/systemd/system/evently-bot.service`

```ini
[Unit]
Description=Evently Telegram Bot Daemon
After=network.target evently-web.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Project-evently/evently
EnvironmentFile=/home/ubuntu/Project-evently/evently/.env
ExecStart=/home/ubuntu/Project-evently/evently/.venv/bin/python -m bot.main
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Xizmatlarni yoqish va tekshirish:
```bash
sudo systemctl daemon-reload
sudo systemctl start evently-web evently-bot
sudo systemctl enable evently-web evently-bot

# Bot va Web holatini tekshirish:
sudo systemctl status evently-bot
sudo journalctl -u evently-bot -f
```

### 5.5. Nginx va Bepul SSL (Let's Encrypt) ulash
Nginx fayli: `sudo nano /etc/nginx/sites-available/evently`

```nginx
server {
    listen 80;
    server_name <SIZNING_ELASTIC_IP> yourdomain.com;

    client_max_body_size 20M;

    location /static/ {
        alias /home/ubuntu/Project-evently/evently/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Project-evently/evently/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Faollashtirish:
```bash
sudo ln -s /etc/nginx/sites-available/evently /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Agar domeningiz bo'lsa, SSL o'rnatish:
# sudo apt install -y certbot python3-certbot-nginx
# sudo certbot --nginx -d yourdomain.com
```

---

## ⏰ 6-QADAM: Tadbirlar Eslatmasini (Reminders) Cron orqali avtomatlashtirish

Loyihangizdagi `apps/events/management/commands/send_event_reminders.py` buyrug'i 24 soat qolgan tadbirlar bo'yicha Telegram orqali eslatma yuboradi. Buni har soatda avtomatik ishlashi uchun Crontab'ga qo'shamiz:

```bash
crontab -e
```
Fayl oxiriga quyidagilardan birini qo'shing:

```bash
# A) Docker ishlatilsa:
0 * * * * cd /home/ubuntu/Project-evently/evently && docker compose exec -T web python manage.py send_event_reminders >> /var/log/evently_reminders.log 2>&1

# B) Systemd ishlatilsa:
0 * * * * /home/ubuntu/Project-evently/evently/.venv/bin/python /home/ubuntu/Project-evently/evently/manage.py send_event_reminders >> /var/log/evently_reminders.log 2>&1
```

---

## ☁️ 7-QADAM: Muqobil variant: Render.com orqali tezkor deploy

AWS o'rniga bepul/oson bulut kerak bo'lsa:
1. `build.sh`:
   ```bash
   #!/usr/bin/env bash
   set -o errexit
   pip install -r requirements.txt
   python manage.py collectstatic --no-input
   python manage.py migrate
   ```
2. `Procfile`:
   ```yaml
   web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   bot: python -m bot.main
   ```
3. Render'da:
   - **PostgreSQL**: `evently-db` ochiladi.
   - **Web Service**: Build Command: `./build.sh`, Start Command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
   - **Background Worker**: Start Command: `python -m bot.main`

---

## ✅ 8-QADAM: Evently loyihasini tekshirish nazorat ro'yxati (Deployment Checklist)

Deploy amalga oshirilgach, quyidagi amallarni birma-bir sinab ko'ring:

- [ ] **1. Swagger / ReDoc hujjatlari ochilishini tekshirish:**  
  👉 Brauzerda: `http://<SIZNING_IP_YOKI_DOMEN>/api/docs/` ochilishi va barcha endpointlar ro'yxati chiqishi kerak.
- [ ] **2. Jazzmin Admin paneli dizayni:**  
  👉 `http://<SIZNING_IP_YOKI_DOMEN>/admin/` ga kiring. Jazzmin uslublari, piktogrammalar va CSS buzilmasdan yuklanishi shart (`collectstatic` ishlaganini bildiradi).
- [ ] **3. Superuser kirishi:**  
  👉 Superuser login/parolini kiritib, Categories, Events, Registrations bo'limlarini boshqara olishingizni tekshiring.
- [ ] **4. Telegram Bot /start buyrug'i:**  
  👉 Telegram ilovasida `@myeventlyBot` ga `/start` yuboring. Javob xabari va menyular chiqishi kerak.
- [ ] **5. Telegram Bot orqali profil bog'lash va /my_events:**  
  👉 Web sayt yoki API orqali berilgan token bilan `/start <token>` qilib ko'ring. Tizimga bog'langanidan so'ng `/my_events` buyrug'i bilan chiptalarni ko'rishni tekshiring.
- [ ] **6. Tadbirga ro'yxatdan o'tganda xabarnoma kelishi:**  
  👉 Biror tadbirga ro'yxatdan o'ting (`/api/v1/registrations/`). Telegram botingizga darhol tasdiq xabari (`notify_registration_success`) kelishi kerak.
- [ ] **7. Xavfsizlik:**  
  👉 `.env` da `DEBUG=False` bo'lishi va AWS Security Group'da 5432-port tashqi dunyoga yopiq ekanligiga ishonch hosil qiling.

---

🎉 **Endi Evently loyihangiz AWS bulutida to'liq xavfsiz va barqaror ishlamoqda!**
