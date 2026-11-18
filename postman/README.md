# Evently API — Postman To'plami Qo'llanmasi

Ushbu papkada **Evently** backend loyihasining `README.md` hujjatida ko'rsatilgan barcha REST API endpointlarini qulay test qilish uchun tayyorlangan Postman to'plami joylashgan.

---

## 📁 Fayllar

1. **`Evently_API.postman_collection.json`** — Barcha 16+ ta API so'rovlari jamlangan Postman Collection (v2.1).
2. **`Evently_Local.postman_environment.json`** — Lokal server uchun muhit o'zgaruvchilari (`baseUrl`, avtomatik `accessToken`, `adminAccessToken`, `eventId`, va h.k.).

---

## 🚀 Postmanga Qanday Import Qilinadi?

1. **Postman** dasturini oching.
2. Chap yuqori burchakdagi **`Import`** tugmasini bosing (yoki `Ctrl + O`).
3. Ushbu `postman/` papkasidagi har ikkala faylni tanlang:
   - `Evently_API.postman_collection.json`
   - `Evently_Local.postman_environment.json`
4. Postman o'ng yuqori burchagidagi muhitlar ro'yxatidan (Environment dropdown) **`Evently Local Environment`** ni tanlang.

---

## ⚡ Avtomatlashtirilgan Imkoniyatlar (Test Scripts)

Kolleksiyadagi ba'zi so'rovlarda maxsus skriptlar yozilgan bo'lib, ular token yoki ID'larni qo'lda ko'chirib yurish zaruriyatini yo'qotadi:

1. **`01. Authentication -> Login (User)`**:
   - Muvaffaqiyatli login qilinganda, response'dan `access` va `refresh` tokenlarni olib, avtomatik `{{accessToken}}` va `{{refreshToken}}` o'zgaruvchilariga yozib qo'yadi.
   - Keyingi barcha user so'rovlari (`auth/me/`, `register for event`, `telegram/link/`) avtomatik shu tokendan foydalanadi.

2. **`01. Authentication -> Login (Admin)`**:
   - Admin sifatida login qilinganda, `{{adminAccessToken}}` o'zgaruvchisiga saqlanadi.
   - Admin amallari (`Create Event`, `Update Event`, `Close Event`, `Participants`) avtomatik admin tokeni bilan ishlaydi.

3. **`02. Events -> Create Event (Admin)`**:
   - Yangi tadbir yaratilganda, uning `id` sini avtomatik `{{eventId}}` o'zgaruvchisiga o'rnatadi. Keyingi batafsil ko'rish, tahrirlash yoki yozilish so'rovlarida ID qo'lda kiritilishi shart emas.

4. **`04. Telegram -> 1. Get Telegram Link Token`**:
   - Generatsiya qilingan havoladagi unikal tokenni (`start=<token>`) ajratib olib, `{{telegramLinkToken}}` o'zgaruvchisiga o'rnatadi. 2-qadamdagi bot so'rovi ushbu tokenni avtomatik ishlatadi.

---

## 🔄 Tavsiya Etilgan Testlash Ketma-ketligi

### 1-qadam: Foydalanuvchi va Admin ro'yxatdan o'tishi
- `POST /api/v1/auth/register/` orqali yangi foydalanuvchi yarating.
- `POST /api/v1/auth/login/` orqali tizimga kiring (`{{accessToken}}` saqlanadi).
- Django orqali admin foydalanuvchi yarating (`python manage.py createsuperuser`) va `Login (Admin)` orqali kiring (`{{adminAccessToken}}` saqlanadi).

### 2-qadam: Tadbir yaratish (Admin)
- `POST /api/v1/events/` (Create Event) so'rovini yuboring.
- Yangi tadbir ID'si avtomatik `{{eventId}}` ga saqlanadi.

### 3-qadam: Ro'yxatdan o'tish (User)
- `POST /api/v1/events/{{eventId}}/register/` so'rovi orqali tadbirga yoziling.
- `GET /api/v1/me/registrations/` orqali yozilgan tadbirlaringizni tekshiring.
- Admin sifatida `GET /api/v1/events/{{eventId}}/participants/` orqali qatnashuvchilar ro'yxatini ko'ring.

### 4-qadam: Telegram Integratsiyasi
- `POST /api/v1/telegram/link/` orqali bog'lash tokenini oling.
- `POST /api/v1/telegram/confirm/` orqali bot nomidan tasdiqlang.
