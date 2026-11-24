# 🐳 10-BOSQICH (PHASE 10): SERVERGA YUKLASHGA TAYYORLASH VA DOCKERLASHTIRISH (PRE-DEPLOYMENT GUIDE)

> **Mentor so'zi:**  
> "Ukam / do'stim, tabriklayman! Sen loyihaning barcha asosiy funksiyalarini (Users, Events, Registrations, Notifications, Telegram Bot) yozib bo'lding. Endi 10-bosqich — **Deployment (Serverga chiqarish)** ga keldik!  
> Loyihani to'g'ridan-to'g'ri serverga tashlashdan oldin, uni **server muhitiga tayyorlash (pre-deployment)** kerak. Buning uchun:
> 1. Statik fayllar (Jazzmin admin CSS) serverda ishlashi uchun **WhiteNoise** va **Gunicorn** ulanadi;
> 2. `settings.py` ga production xavfsizlik sozlamalari kiritiladi;
> 3. Tizim to'liq **Docker va Docker Compose** ga o'raladi (Web, Bot, Baza bitta yaxlit mexanizmga aylanadi);
> 4. Lokal kompyuteringda konteynerlarni bir marta yurgizib, hammasi xatosiz ishlayotganiga ishonch hosil qilinadi;
> 5. So'ngra serverga (AWS ga) birgina `git clone` va `docker compose up` bilan uzatiladi.  
> 
> Quyida aynan nima ish qilish kerakligi, qaysi faylga qanday kod yozilishi va nima sababdan yozilishi qadamma-qadam, tartib bilan keltirilgan. Boshladik!"

---

## 📌 QADAMMA-QADAM HARAKATLAR XARITASI

```
[1-Qadam: Gunicorn va WhiteNoise o'rnatish]
                    ⬇
[2-Qadam: settings.py ga Production sozlamalarini kiritish]
                    ⬇
[3-Qadam: .dockerignore faylini yaratish]
                    ⬇
[4-Qadam: Dockerfile faylini yaratish]
                    ⬇
[5-Qadam: docker-compose.yml faylini yaratish]
                    ⬇
[6-Qadam: .env faylini Docker va Production uchun to'g'rilash]
                    ⬇
[7-Qadam: Lokal Docker'da tekshirish (Test Run)]
                    ⬇
[8-Qadam: Git orqali Serverga yuklashga tayyorlash]
```

---

## 🛠 1-QADAM: Production Kutubxonalarini O'rnatish (Gunicorn va WhiteNoise)

### ❓ Bu nima va nima uchun kerak?
- **Gunicorn (Green Unicorn):** Django'ning `python manage.py runserver` buyrug'i faqat ishlab chiqish (development) uchun mo'ljallangan, u bir vaqtning o'zida ko'p foydalanuvchini ko'tara olmaydi. `gunicorn` esa productionda bir necha ishchi oqim (workers) ochib, minglab so'rovlarni barqaror qabul qiluvchi professional WSGI serverdir.
- **WhiteNoise:** Django productionda (`DEBUG=False` bo'lganda) o'zining statik fayllarini (CSS, JavaScript, Jazzmin rasmlari) tarqatishni to'xtatadi. `whitenoise` Nginx'siz ham Djangoning o'zidan statik fayllarni siqilgan va keshlashtirilgan holda chaqmoqdek tez tarqatish imkonini beradi.

### 📝 Bajariladigan ish:
Loyihangiz terminalida (`evently` papkasida) quyidagi buyruqni bering:

```bash
uv add gunicorn whitenoise
```

*Eslatma: Agar serverda pip ishlatilsa, requirements.txt yangilanadi:*
```bash
uv pip compile pyproject.toml -o requirements.txt
```

---

## ⚙️ 2-QADAM: `config/settings.py` Fayliga Production Sozlamalarini Kiritish

### ❓ Bu yerda nima o'zgaradi va nima uchun?
1. **WhiteNoise Middleware:** Statik fayllarni tutib olib foydalanuvchiga uzatadi.
2. **`STATIC_ROOT`:** `python manage.py collectstatic` buyrug'i barcha ilovalardagi CSS/JS fayllarni bitta papkaga yig'ishi uchun kerak.
3. **`CSRF_TRUSTED_ORIGINS` va `CORS_ALLOWED_ORIGINS`:** Brauzerdan so'rov yuborilganda 403 Forbidden xatosi bermasligi uchun.

### 📝 Bajariladigan ish: `config/settings.py` fayliga quyidagi qismlarni qo'shing:

#### 1) `MIDDLEWARE` ga WhiteNoise qo'shish:
`SecurityMiddleware` dan keyin darhol WhiteNoise middleware'ini joylashtiring:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- SHU YERGA QO'SHILADI!
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

#### 2) Statik va Media sozlamalarini to'ldirish:
Faylning `STATIC_URL = 'static/'` qismini topib, quyidagicha to'ldiring:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise statik fayllarni siqish va xotirada keshlashtirish
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media fayllar (Tadbirlar rasmlari, foydalanuvchilar yuklagan fayllar)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### 3) Xavfsizlik, CSRF va CORS sozlamalari:
`ALLOWED_HOSTS` pastiga quyidagi sozlamalarni qo'shing:

```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# HTTPS/Nginx orqasida to'g'ri ishlashi uchun:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF ruxsat berilgan domenlar
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS", 
    default=["http://localhost:8000", "http://127.0.0.1"]
)

# CORS sozlamasi (Frontend so'rovlariga ruxsat)
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://localhost:5173"]
)
```

---

## 🚫 3-QADAM: `.dockerignore` Faylini Yaratish

### ❓ Bu nima va nima uchun kerak?
Docker image qurilayotganda kompyuterdagi `.venv` (virtual muhit), `.git`, kesh fayllar (`__pycache__`) va lokal `.env` konteyner ichiga ko'chib o'tib ketmasligi kerak. Aks holda image hajmi juda kattalashib ketadi va xatolar keltirib chiqaradi.

### 📝 Bajariladigan ish:
Loyiha ildizida (`C:\Users\User\summer_python2026\Project-evently\evently\.dockerignore`) fayl oching va quyidagi kodni yozing:

```text
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
.env
.pytest_cache/
tests/
Dockerfile
docker-compose.yml
plan.md
plan01.md
postman/
*.log
```

---

## 📦 4-QADAM: `Dockerfile` Faylini Yaratish

### ❓ Bu nima va nima uchun kerak?
`Dockerfile` — bu bizning dasturimiz uchun operatsion tizim (Linux Debian), Python 3.11, `uv` paket menejeri va dasturning barcha kutubxonalarini avtomat tarzda qadamma-qadam o'rnatib beruvchi retsept/instruksiya faylidir.

### 📝 Bajariladigan ish:
Loyiha ildizida (`evently/Dockerfile`) fayl yarating va quyidagi to'liq kodni yozing:

```dockerfile
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
```

---

## 🚢 5-QADAM: `docker-compose.yml` Faylini Yaratish

### ❓ Bu nima va nima uchun kerak?
Bizning loyihamizda 3 ta mustaqil xizmat bor:
1. **`db`**: PostgreSQL ma'lumotlar bazasi;
2. **`web`**: Django REST API + Jazzmin Admin paneli (Gunicorn orqali);
3. **`bot`**: Aiogram Telegram Boti (`python -m bot.main`).

`docker-compose.yml` fayli ushbu 3 ta xizmatni bitta umumiy tarmoqqa (`evently_network`) birlashtiradi, ularni bir-biri bilan bog'laydi va bitta `docker compose up` buyrug'i bilan bir vaqtda ishga tushirish imkonini beradi.

### 📝 Bajariladigan ish:
Loyiha ildizida (`evently/docker-compose.yml`) fayl yarating va quyidagi to'liq kodni yozing:

```yaml
version: '3.8'

services:
  # ==========================================
  # 1. POSTGRESQL MA'LUMOTLAR BAZASI
  # ==========================================
  db:
    image: postgres:16-alpine
    container_name: evently_postgres
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME:-evently_db}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres_password_123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - evently_network

  # ==========================================
  # 2. DJANGO WEB API & JAZZMIN ADMIN
  # ==========================================
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

  # ==========================================
  # 3. AIOGRAM TELEGRAM BOT
  # ==========================================
  bot:
    build: .
    container_name: evently_bot
    restart: always
    command: python -m bot.main
    env_file:
      - .env
    environment:
      # Bot backendga konteyner ichki tarmog'i orqali ulanadi:
      - BACKEND_API_URL=http://web:8000/api/v1
    depends_on:
      - web
    networks:
      - evently_network

# Volume'lar (Ma'lumotlar saqlanib qolishi uchun)
volumes:
  postgres_data:
  static_volume:
  media_volume:

# Umumiy ichki tarmoq
networks:
  evently_network:
    driver: bridge
```

---

## 🔐 6-QADAM: `.env` Faylini Docker va Production Uchun Moslash

### ❓ Nimaga e'tibor berish kerak?
- Docker muhitida Django bazaga ulanishi uchun `DB_HOST=db` bo'lishi kerak (`localhost` emas, chunki baza `db` nomli servisda ishlaydi).
- Bot backendga ulanishi uchun `BACKEND_API_URL=http://web:8000/api/v1` bo'lishi shart.
- `BOT_API_SECRET` backend va bot o'rtasidagi so'rovlarni himoya qilish uchun ikkalasida bir xil bo'lishi shart.

### 📝 Bajariladigan ish: Serverda (yoki Docker ishlatilganda) `.env` fayl namunasi:

```env
# Django Asosiy
DEBUG=False
SECRET_KEY=xqzr6m-=8wpk-=khsy8m&)0ano1!_@w4#%tszydwk44lw+2g&3-super-secret-key-prod
ALLOWED_HOSTS=*,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
TIME_ZONE=Asia/Tashkent

# Database (Docker compose uchun)
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

# Telegram Bot
TELEGRAM_BOT_TOKEN=9230877104:AAEMtZJuZcuVL1rYM1wAKdrgQQfyWDwSuRo
TELEGRAM_BOT_USERNAME=myeventlyBot
BOT_API_SECRET=WNYUTp-YkgvHGELCTVlq2BjioJ3mPwkr8mBs4Cb7h7s
BACKEND_API_URL=http://web:8000/api/v1

# Reminders
REMINDER_HOURS_BEFORE=24
```

---

## 🧪 7-QADAM: Lokal Kompyuterda Docker Orqali Sinovdan O'tkazish (Test Run)

Serverga chiqishdan oldin o'zingizning kompyuteringizda Docker Desktop yoqilgan holda hamma narsani tekshirib ko'ring:

### 1) Loyihani konteynerda qurish va ishga tushirish:
```bash
docker compose up -d --build
```
*Bu buyruq `Dockerfile` asosida image quradi, Postgres, Web va Bot konteynerlarini ishga tushiradi, avtomatik `collectstatic` va `migrate` qiladi.*

### 2) Admin (Superuser) yaratish:
```bash
docker compose exec web python manage.py createsuperuser
```
*Admin username, email va parolni kiriting.*

### 3) Loglarni tekshirish:
```bash
# Telegram Bot logi:
docker compose logs -f bot
# Natijada: "Evently Telegram Bot ishga tushmoqda..." chiqishi kerak!

# Web API logi:
docker compose logs -f web
```

### 4) Brauzerda tekshirish:
- **Swagger API hujjati:** `http://localhost:8000/api/docs/` ochilishi kerak.
- **Jazzmin Admin paneli:** `http://localhost:8000/admin/` dizayn va stillar buzilmasdan chiqishi kerak.
- **Telegram Bot:** Telegramda `@myeventlyBot` ga `/start` yuborib javob oling.

### 5) Eslatmalar (Reminders) buyrug'ini Docker ichida sinab ko'rish:
```bash
docker compose exec web python manage.py send_event_reminders
```
*Natijada konsolda: `0 ta eslatma muvaffaqiyatli yuborildi.` (yoki eslatmalar yuborilgani) chiqsa, demak buyruq Docker ichida to'liq xatosiz ishlamoqda!*

### 6) Sinov tugagach to'xtatish:
```bash
docker compose down
```

---

## 🚀 8-QADAM: Git Orqali Serverga (AWS EC2) Yuklash Ketma-ketligi

Lokalda barcha fayllar tayyor bo'lgach, serverga yuklash jarayoni 4 ta oson qadamdan iborat bo'ladi:

### 1) Kodlarni Git orqali GitHub'ga jo'natish:
```bash
git add .
git commit -m "feat: Add Dockerfile, docker-compose and production settings for deployment"
git push origin develop
```

### 2) AWS EC2 serveriga SSH orqali kirish:
```bash
ssh -i "evently-key.pem" ubuntu@<SIZNING_AWS_ELASTIC_IP>
```

### 3) Serverda loyihani tortib olish:
```bash
git clone https://github.com/<sizning-repo>/Project-evently.git
cd Project-evently/evently
nano .env   # (Yuqoridagi 6-qadamdagi .env qiymatlarini kiritasiz)
```

### 4) Serverda ishga tushirish:
```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

---

## ⏰ 9-QADAM: Serverda Tadbirlar Eslatmasini (Reminders Crontab) Avtomatlashtirish

Loyihangiz AWS serverida ishga tushgach, foydalanuvchilarga tadbir boshlanishidan 24 soat oldin bot orqali avtomatik eslatma borishi uchun serverning **Crontab** jadvaliga qo'shib qo'yiladi.

### 📝 Serverda bajariladigan ish:
AWS EC2 serveringiz terminalida:
```bash
crontab -e
```
*(Agar birinchi marta kirayotgan bo'lsangiz, muharrir sifatida `1` (nano) ni tanlang).*

Faylning eng pastki qatoriga quyidagi buyruqni yozing:

```bash
# Har soat boshida tadbirlar eslatmasini avtomatik yuborish:
0 * * * * cd /home/ubuntu/Project-evently/evently && docker compose exec -T web python manage.py send_event_reminders >> /var/log/evently_reminders.log 2>&1
```

Faylni saqlash uchun: `Ctrl + O`, `Enter` va chiqish uchun `Ctrl + X`.

Endi server har soatda ushbu buyruqni o'zi orqa fonda avtomatik chaqiradi va foydalanuvchilaringiz tadbirni o'tkazib yubormasligi uchun doimiy eslatma olib turishadi!

---

## 📋 YAKUNIY NAZORAT RO'YXATI (DEPLOYMENT GA TAYYORLIK)

- [ ] `gunicorn` va `whitenoise` o'rnatildi (`uv add gunicorn whitenoise`).
- [ ] `config/settings.py` ga WhiteNoise middleware va `STATIC_ROOT` qo'shildi.
- [ ] `.dockerignore` fayli yaratildi.
- [ ] `Dockerfile` yaratildi.
- [ ] `docker-compose.yml` yaratildi.
- [ ] `.env` da `DB_HOST=db` va `BACKEND_API_URL=http://web:8000/api/v1` to'g'rilandi.
- [ ] `docker compose up -d --build` orqali lokalda sinab ko'rildi.
- [ ] `send_event_reminders` buyrug'i lokal Dockerda sinab ko'rildi.
- [ ] GitHub'ga push qilindi va AWS serverda ishga tushirildi.
- [ ] Serverda `crontab -e` orqali eslatmalar avtomatlashtirildi.

---
🎯 **Endi sizning Evently loyihangiz to'liq Dockerlashtirildi va istalgan Linux/AWS serverda bir necha daqiqada ishga tushishga tayyor!**
