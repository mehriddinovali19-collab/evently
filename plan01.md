# Evently — Professional Backend Dasturchi Uchun Yo'l Xaritasi (Mentor Guide)

> **Mentor so'zi:**  
> "Ukam / do'stim, ushbu qo'llanmada senga tayyor kodlar **berilmaydi**. Nega bilasanmi? Chunki tayyor kodni shunchaki nusxalab qo'yish (copy-paste) seni dasturchi qilmaydi. Haqiqiy Senior backendchi kod yozishdan oldin **arxitekturani tushunadi**, **kutubxonalarni to'g'ri tanlaydi** va har bir yozgan satri uchun javob bera oladi.  
> Bu reja — sening kompassing. Men senga har bir bosqichda nima qilish kerakligini, qaysi kutubxonalardan qanday maqsadda foydalanishni, qanday biznes xatolar va tuzoqlarga tushmaslik kerakligini o'rgataman. Kodni esa o'z qo'llaring bilan, hujjatlarni (documentation) o'qib, o'ylab yozasan. Qani, boshladik!"

---

## 📌 Status Belgilari (O'zingiz belgilab boring)
- `[ ]` — Hali boshlanmagan
- `[/]` — Jarayonda
- `[x]` — Bajarildi, sinovdan o'tdi va git commit qilindi

---

## 🧰 Umumiy Texnologiyalar Steki va Kutubxonalar

Loyiha davomida biz quyidagi vositalardan foydalanamiz. Har birining o'z o'rni va vazifasi bor:

| Kutubxona / Texnologiya | Versiya / Standart | Nimaga aynan shu? (Mentordan izoh) |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Zamonaviy sintaksis, xatoliklarni aniq ko'rsatish va tezlik. |
| **Django** | 5.0+ | Kuchli ORM, admin panel, xavfsizlik choralari va ishonchli arxitektura. |
| **Django REST Framework (DRF)** | 3.15+ | Standart RESTful API qurish, serializer'lar va permission'lar uchun sanoat standarti. |
| **djangorestframework-simplejwt** | 5.3+ | Xavfsiz, stateless JWT (JSON Web Token) autentifikatsiyasini oson sozlash. |
| **psycopg (psycopg 3)** | 3.1+ | PostgreSQL bilan ishlash uchun eng yangi, asinxron qo'llab-quvvatlovchi, tezkor drayver. |
| **django-environ** | 0.11+ | `.env` orqali 12-Factor App tamoyiliga ko'ra konfiguratsiyani xavfsiz boshqarish. |
| **django-filter** | 24.0+ | REST API'larda dinamik qidiruv va filtrlashni bir necha qatorda tashkil qilish. |
| **django-cors-headers** | 4.3+ | Keyinchalik frontend (React, Vue) ulanganda CORS (Cross-Origin) blokirovkasini oldini olish. |
| **drf-spectacular** | 0.27+ | Zamonaviy OpenAPI 3.0 sxemasi va chiroyli Swagger UI/Redoc yaratish (eskirgan `drf-yasg` o'rniga). |
| **aiogram** | 3.4+ | Asinxron Telegram bot yaratish uchun O'zbekistonda va dunyoda eng mashhur Python kutubxona. |
| **httpx** | 0.27+ | Bot va Backend o'rtasida yoki tashqi API'larga zamonaviy asinxron HTTP so'rovlar yuborish. |
| **pytest & pytest-django** | 8.0+ | Djangoning standart `TestCase`iga qaraganda ancha qulay, o'qilishi oson va tezkor test tizimi. |

---

## 🧭 Loyihaning Bosqichma-bosqich Rejasi (Phases)

```
[Phase 1: Muhit, Baza va Custom User]
                ⬇
[Phase 2: JWT Auth, Profil va Swagger]
                ⬇
[Phase 3: Events CRUD va Maxsus Permission'lar]
                ⬇
[Phase 4: Filter, Qidiruv, Pagination va N+1 Muammosi]
                ⬇
[Phase 5: Registration Tizimi va Race Condition]
                ⬇
[Phase 6: Tadbirdan Chiqish va Statuslar Logikasi]
                ⬇
[Phase 7: Telegram Bot va Deep Linking Integratsiyasi]
                ⬇
[Phase 8: Eslatmalar (Reminders) va Fondagi Vazifalar]
                ⬇
[Phase 9: Pytest bilan Avtomatik Testlash]
                ⬇
[Phase 10: Production, Xavfsizlik va Deployment]
```

---

## 1-BOSQICH: Muhitni sozlash, Loyiha arxitekturasi va Custom User modeli

> **Mentor eslatmasi:**  
> "Django bilan ishlashda eng katta va tuzatib bo'lmas xato — standart `auth.User` bilan `migrate` qilib yuborishdir! Agar loyihani boshida `AbstractUser` orqali Custom User yaratmasang, keyinchalik foydalanuvchiga qo'shimcha maydon (masalan, telefon raqam yoki telegram_chat_id) qo'shish yoki email orqali login qilish juda og'riqli bo'ladi. Biz birinchi qadamdanoq poydevorni to'g'ri qo'yamiz."

### 📚 Foydalaniladigan kutubxonalar:
- `django`: Asosiy web-framework.
- `django-environ`: Maxfiy kalitlar (`SECRET_KEY`, `DB_*`) ni `.env` dan o'qish uchun.
- `psycopg`: PostgreSQL ma'lumotlar bazasiga ulanish uchun.
- `django-cors-headers`: CORS xavfsizlik sozlamalari uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [X] **Virtual muhit va paketlar:** Python virtual muhitini yaratish (`.venv`) va paketlarni o'rnatish.
- [X] **Kataloglar arxitekturasi:** Loyihani tartibli saqlash uchun ilovalarni (apps) alohida `apps/` papkasiga joylashtirish tizimini yo'lga qo'yish (masalan: `apps.users`).
- [X] **Konfiguratsiya va `.env`:** `.env` fayli yaratib, unga `SECRET_KEY`, `DEBUG`, PostgreSQL ulanish parametrlarini, vaqt mintaqasini (`Asia/Tashkent`) kiritish va `settings.py` da bularni o'qib olish.
- [X] **Custom User modeli:**
  - Foydalanuvchi tizimga `username` bilan emas, **`email`** bilan kirishi kerak. Shuning uchun standart `username` maydonini o'chirib, `USERNAME_FIELD = 'email'` qilish kerak.
  - Qo'shimcha maydonlar: `first_name`, `last_name`, `phone_number`, `role` (admin yoki oddiy user), `telegram_chat_id` va `telegram_link_token`.
  - **Custom UserManager:** `create_user` va `create_superuser` metodlarini email asosida ishlaydigan qilib qayta yozish.
- [X] **`AUTH_USER_MODEL`:** `settings.py` da Djangoga yangi modelimizni tanitish.
- [X] **Admin panel:** `UserAdmin` orqali yangi maydonlarni chiroyli ko'rsatish va boshqarish.
- [X] **Birinchi migratsiya va superuser:** Baza jadvallarini hosil qilish va tizimga kirish uchun admin yaratish.

### 💡 Mentordan o'ylash uchun savollar (Self-Reflection):
1. Nega Django standart `createsuperuser` buyrug'i email orqali ishlashi uchun `UserManager` yozishimiz shart bo'ldi?
2. `telegram_chat_id` maydoniga nima uchun `BigIntegerField` tanladik? (Telegram ID'lar oddiy 32-bit Integer chegarasidan oshib ketganmi?)
3. `unique=True` qaysi maydonlarga qo'yilishi shart va nima uchun?

---

## 2-BOSQICH: Autentifikatsiya (JWT), Profil va Swagger (API Hujjatlari)

> **Mentor eslatmasi:**  
> "Biz quryotgan tizim REST API. Bu degani server sessiya (cookie session) saqlamaydi — u **Stateless** bo'lishi kerak. Shuning uchun biz JWT (JSON Web Token) ishlatamiz. Foydalanuvchi login qilganda unga ikkita kalit beriladi: qisqa umrli `access token` (so'rovlar uchun) va uzoq umrli `refresh token` (yangi access olish uchun).  
> Shuningdek, frontendsiz ishlayotganing uchun sening eng yaqin do'sting — Swagger bo'ladi. Har bir yaratgan endpointing Swagger'da ko'rinib turishi shart!"

### 📚 Foydalaniladigan kutubxonalar:
- `djangorestframework`: API ko'rinishlari, Serializer'lar va status kodlar uchun.
- `djangorestframework-simplejwt`: Access va Refresh token mexanizmi uchun.
- `drf-spectacular`: Avtomatik OpenAPI 3.0 hujjatlashtirish va Swagger UI interfeysi uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **DRF va SimpleJWT sozlamalari:**
  - `REST_FRAMEWORK` sozlamalarida standart autentifikatsiya sifatida `JWTAuthentication` ni belgilash.
  - Tokenlarning yashash muddatini belgilash (Access: masalan, 60 daqiqa; Refresh: masalan, 7 kun).
- [ ] **Foydalanuvchi ro'yxatdan o'tishi (Register API):**
  - Foydalanuvchidan email, ism, familiya, telefon va ikkita parol (`password`, `password_confirm`) qabul qilish.
  - Parollarning bir xilligini va Djangoning standart parol xavfsizligi qoidalariga (`validate_password`) mos kelishini tekshirish.
  - Yangi foydalanuvchini bazada xavfsiz hash qilingan parol bilan saqlash.
- [ ] **Login va Token yangilash (Login & Refresh API):**
  - Email va parol yuborilganda `access` va `refresh` tokenlar qaytarish.
  - Refresh token orqali yangi access token olish endpointini ulash.
- [ ] **Profil boshqaruvi (`/auth/me/`):**
  - Tizimga kirgan foydalanuvchining o'z ma'lumotlarini ko'rish (`GET`) va tahrirlash (`PATCH`) imkoniyati.
  - Bu endpoint faqat tokeni bor foydalanuvchilarga ochilishi kerak (`IsAuthenticated`).
- [ ] **Swagger UI va Redoc integratsiyasi:**
  - `drf-spectacular` orqali `/api/schema/`, `/api/docs/` (Swagger) va `/api/redoc/` marshrutlarini sozlash.
  - Swagger orqali "Authorize" tugmasi bilan `Bearer <token>` kiritib, barcha endpointlarni brauzerda sinab ko'rish imkonini yaratish.

### 💡 Mentordan o'ylash uchun savollar:
1. Nima uchun parolni hech qachon response'da qaytarib yubormaslik kerak (`write_only=True`)?
2. Agar access token o'g'irlansa nima bo'ladi va uning umrini nima uchun qisqa qilamiz?
3. SimpleJWT standart loginida `username` talab qiladi. Biz `email` orqali login qilish uchun serializer yoki tokenni qanday moslashtirishimiz kerak?

---

## 3-BOSQICH: Tadbirlar (Events) Moduli, CRUD va Maxsus Huquqlar (Permissions)

> **Mentor eslatmasi:**  
> "Endi loyihaning asosiy biznes domeniga keldik — Tadbirlar (Events). Bu yerda kim nima qila olishini qat'iy ajratishimiz kerak. Oddiy foydalanuvchi faqat tadbirlarni ko'ra olishi kerak, ammo yangi tadbir yaratish, uni o'zgartirish yoki o'chirish faqat **Admin** roliga ega shaxslarga ruxsat etiladi. Ruxsatlarni faqat frontendda emas, backendda toshdek mustahkam qilib cheklash shart!"

### 📚 Foydalaniladigan kutubxonalar:
- `djangorestframework`: GenericAPIView'lar, ViewSet'lar va BasePermission sinflari.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Event modelini loyihalash:**
  - Maydonlar: `title`, `description`, `date` (tadbir o'tkaziladigan sana va vaqt), `location` (manzil), `capacity` (maksimal qatnashchilar soni), `status` (ochiq, to'lgan, bekor qilingan, yakunlangan), `created_by` (tashkilotchi / admin).
  - Yaratilgan va o'zgartirilgan vaqtlarni qayd etuvchi `created_at` va `updated_at` maydonlari.
- [ ] **Tadbir modelining validatsiyasi:**
  - Tadbir sanasi o'tmishda bo'lishi mumkin emas! Faqat kelajakdagi sana qabul qilinishi kerak.
  - Sig'im (`capacity`) musbat son bo'lishi kerak (kamida 1 ta).
- [ ] **Maxsus Huquq (Custom Permission):**
  - Yangi permission yozish: masalan, `IsAdminUserRole`. U foydalanuvchining `role == 'admin'` yoki `is_staff=True` ekanligini tekshiradi.
  - O'qish (GET) so'rovlari barcha uchun ochiq (`AllowAny` yoki `IsAuthenticatedOrReadOnly`), lekin o'zgartirish (POST, PUT, PATCH, DELETE) faqat adminlar uchun.
- [ ] **CRUD API'larini yaratish:**
  - Barcha tadbirlar ro'yxatini olish va yangi yaratish (`GET/POST /api/v1/events/`).
  - Bitta tadbirni ko'rish, tahrirlash va o'chirish (`GET/PUT/PATCH/DELETE /api/v1/events/{id}/`).
  - Yangi tadbir yaratilayotganda `created_by` maydoniga avtomatik ravishda so'rov yuborgan adminni biriktirish (`serializer.save(created_by=self.request.user)`).

### 💡 Mentordan o'ylash uchun savollar:
1. Djangodagi `is_staff` bilan biz yaratgan `role == 'admin'` o'rtasida qanday farq bor va ularni qanday uyg'unlashtirish to'g'ri bo'ladi?
2. Agar admin tadbir sig'imini (`capacity`) 50 tadan 30 taga kamaytirmoqchi bo'lsa, lekin allaqachon 40 kishi ro'yxatdan o'tib bo'lgan bo'lsa nima bo'ladi? Buni serializer'da qanday ushlash mumkin?

---

## 4-BOSQICH: Qidiruv, Filtrlash, Pagination va Query Optimizatsiyasi (N+1 Muammosi)

> **Mentor eslatmasi:**  
> "Junior dasturchilar ko'pincha: 'Endpoint ishlayapti-ku, bo'ldi-da!' deb o'ylashadi. Lekin bazada 10 000 ta tadbir bo'lsa va har bir tadbir bilan uning tashkilotchisi yoki ro'yxatdan o'tganlar sonini tortib olayotganda 10 000 ta ortiqcha SQL so'rov ketsa — serveringiz yiqiladi! Bu kasallik **N+1 muammosi** deyiladi. Biz ushbu bosqichda so'rovlarni optimallashtiramiz va frontend uchun qulay filtrlashni ulaymiz."

### 📚 Foydalaniladigan kutubxonalar:
- `django-filter`: Query parametrlari bo'yicha kuchli filtrlash tizimi.
- `rest_framework.filters`: `SearchFilter` va `OrderingFilter` uchun.
- `rest_framework.pagination`: Sahifalash mexanizmi uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Pagination (Sahifalash):**
  - Ro'yxat so'rovlariga sahifalash qo'shish (masalan, sahifada 10 tadan).
  - Response formatida: umumiy soni (`count`), keyingi sahifa (`next`), oldingi sahifa (`previous`) va natijalar (`results`) bo'lishini ta'minlash.
- [ ] **Filterlash va Qidiruv (Filtering & Search):**
  - **Sana bo'yicha filter:** kelayotgan tadbirlar, ma'lum sanalar oralig'idagi tadbirlar.
  - **Status bo'yicha filter:** ochiq (`open`), to'lgan (`full`), yopilgan (`cancelled`/`completed`).
  - **Matnli qidiruv:** Tadbir nomi (`title`) va tavsifi (`description`) bo'yicha `icontains` qidiruvi.
  - **Tartiblash (Ordering):** Sana bo'yicha o'sish yoki kamayish tartibida saralash.
- [ ] **SQL Query Optimizatsiyasi (N+1 ni yo'qotish):**
  - Har bir tadbir bilan birga uning tashkilotchisini (`created_by`) bitta SQL so'rov bilan olib kelish uchun **`select_related`** dan foydalanish.
  - Har bir tadbirga ro'yxatdan o'tgan tasdiqlangan qatnashchilar sonini hisoblash uchun Python loop'i o'rniga ma'lumotlar bazasi darajasida **`annotate(registered_count=Count(...))`** ishlatish.
- [ ] **Bo'sh joylar hisob-kitobi (Dynamic Fields):**
  - Serializer'da har bir tadbir uchun `available_seats` (bo'sh qolgan joylar soni: `capacity - registered_count`) maydonini hisoblab qaytarish.

### 💡 Mentordan o'ylash uchun savollar:
1. `select_related` bilan `prefetch_related` o'rtasidagi farq nima? Qaysi biri `ForeignKey` uchun, qaysi biri `ManyToMany` uchun ishlatiladi?
2. Nega `len(event.registrations.all())` deb yozish juda yomon amaliyot hisoblanadi va uning o'rniga nima ishlatish kerak?

---

## 5-BOSQICH: Ro'yxatdan o'tish (Registration) Tizimi va Race Condition Muammosi

> **Mentor eslatmasi:**  
> "Mana bu haqiqiy backend imtihoni! Tasavvur qil: mashhur tadbirda atigi **1 ta bo'sh joy** qoldi. Aynan bir millisekundda 10 kishi 'Ro'yxatdan o'tish' tugmasini bosdi. Agar sen shunchaki: `if event.available_seats > 0: create_registration()` deb yozsang — nima bo'ladi? Barcha 10 ta so'rov `if` shartidan o'tib ketadi va 1 ta joyga 10 kishi yozilib, sig'im buziladi! Bu xatolik **Race Condition** deyiladi.  
> Bu bosqichda biz tranzaksiya va bazadagi qulflash (Database Locks) orqali ushbu muammoni professional darajada yengamiz."

### 📚 Foydalaniladigan kutubxonalar:
- `django.db.transaction`: Atomar tranzaksiyalar (`atomic`) va qatorlarni qulflash (`select_for_update`) uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Registration oraliq modelini yaratish:**
  - Aloqalar: `user` (Foydalanuvchi) va `event` (Tadbir).
  - Qo'shimcha maydonlar: `status` (tasdiqlangan: `confirmed`, bekor qilingan: `cancelled`), `registered_at` (ro'yxatdan o'tgan vaqt).
  - **Muhim cheklov (Constraint):** Bitta foydalanuvchi bitta tadbirga bir vaqtda faqat bir marta yozilishi mumkin (`UniqueConstraint` user va event bo'yicha).
- [ ] **Ro'yxatdan o'tish logikasi va tekshiruvlar (Validations):**
  - Foydalanuvchi autentifikatsiyadan o'tgan bo'lishi shart.
  - Tadbir statusi `open` holatda bo'lishi shart.
  - Tadbirning o'tkazilish vaqti o'tib ketmagan bo'lishi shart.
  - Foydalanuvchi bu tadbirga avval ro'yxatdan o'tib, hali faol holatda bo'lmasligi kerak.
- [ ] **Race Condition'ni oldini olish mexanizmi:**
  - Jarayonni `transaction.atomic()` bloki ichiga olish.
  - Tadbir ma'lumotini bazadan o'qiyotganda **`select_for_update()`** orqali bazadagi ushbu qatorni (row) boshqa so'rovlar uchun vaqtincha muzlatib (lock) turish.
  - Qulflangan holatda joriy ro'yxatdan o'tganlar sonini qayta sanash va `capacity` bilan solishtirish.
  - Agar joy qolmagan bo'lsa — xatolik (HTTP 400 Bad Request) qaytarish va tadbir statusini avtomatik `full` ga o'zgartirish.
  - Joy bo'lsa — `Registration` obyektini yaratish va tranzaksiyani yakunlash.

### 💡 Mentordan o'ylash uchun savollar:
1. `transaction.atomic()` o'zi nima qiladi? Agar kod o'rtasida kutilmagan xatolik chiqsa bazaga nima bo'ladi?
2. `select_for_update()` nima uchun faqat `transaction.atomic()` ichida ishlashi shart?
3. Bazadagi `UniqueConstraint` bilan koddagi `if Registration.objects.filter(...).exists()` tekshiruvi nega ikkalasi ham birga bo'lishi kerak?

---

## 6-BOSQICH: Tadbirdan Chiqish, Shaxsiy Ro'yxatlar va Tadbirni Yopish

> **Mentor eslatmasi:**  
> "Hayotda rejalar o'zgaradi: odamlar tadbirga bora olmay qolishi mumkin. Ular o'z vaqtida ro'yxatdan chiqib ketsa, ularning o'rniga boshqa bir odam kira olishi kerak. Bu bosqichda biz 'bekor qilish' (cancellation) va admin tomonidan tadbirni majburiy yopish logikasini quramiz."

### 📚 Foydalaniladigan kutubxonalar:
- `djangorestframework`: Maxsus action'lar (`@action`), serializer metodlari va status kodlar.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Tadbirdan chiqish (Cancel Registration API):**
  - Endpoint: Foydalanuvchi o'zi ro'yxatdan o'tgan tadbirni bekor qilishi (`DELETE` yoki `POST /registrations/{id}/cancel/`).
  - Hard delete (bazadan butunlay o'chirib yuborish) o'rniga **Soft delete** (statusni `cancelled` ga o'tkazish) tavsiya etiladi — shunda kim qachon bekor qilgani tarixi saqlanib qoladi.
  - Tadbir sanasi o'tib ketgan bo'lsa, ro'yxatdan chiqishga ruxsat berilmaydi!
  - Bekor qilingandan so'ng bo'sh joylar soni avtomatik ravishda bittaga ko'payadi va agar tadbir `full` bo'lib turgan bo'lsa, uning statusi yana qayta `open` holatiga o'tadi.
- [ ] **Mening tadbirlarim (`/api/v1/registrations/my/`):**
  - Tizimga kirgan foydalanuvchining faqat o'ziga tegishli barcha ro'yxatdan o'tish arizalari ro'yxatini qaytarish.
  - Qulaylik uchun har bir arizaning ichida tadbirning to'liq ma'lumotlari (`EventSerializer`) ko'rinib turishi kerak.
- [ ] **Admin: Tadbirni muddatidan oldin yopish (`/events/{id}/close/`):**
  - Faqat adminlar uchun maxsus endpoint.
  - Tadbir statusini `cancelled` yoki `completed` ga o'tkazish.
  - Yopilgan tadbirlarga boshqa hech kim ro'yxatdan o'ta olmasligi shart.

### 💡 Mentordan o'ylash uchun savollar:
1. Nima uchun moliyaviy, booking va e-commerce tizimlarida `delete()` o'rniga statusni o'zgartirish (Soft delete) qo'llaniladi?
2. Agar tadbir boshlanishiga 1 soat qolgan bo'lsa, chiqishga ruxsat berish kerakmi yoki yo'q? Bu biznes qoidani qanday chegaralash mumkin?

---

## 7-BOSQICH: Telegram Bot Integratsiyasi va Hisobni Bog'lash (Deep-Linking)

> **Mentor eslatmasi:**  
> "Ko'pchilik havaskorlar xato qilib Telegram bot kodini Django view'larining ichiga tiqib yuborishadi yoki aksincha. Bu butunlay noto'g'ri!  
> Bizning Telegram botimiz — bu **alohida asinxron mikroxizmat**. U Django bazasiga to'g'ridan-to'g'ri kirmaydi, balki biz yaratgan REST API bilan `httpx` orqali xuddi frontend kabi muloqot qiladi.  
> Eng qiziq nuqta — foydalanuvchi saytdagi akkaunti bilan Telegram akkauntini qanday bog'laydi? Buni xavfsiz **Deep-Linking** mexanizmi orqali amalga oshiramiz."

### 📚 Foydalaniladigan kutubxonalar:
- `aiogram` (v3.x): Asinxron Telegram bot frameworki (Router'lar, Handler'lar).
- `httpx`: Asinxron rejimda Backend API'ga HTTP so'rovlar yuboruvchi zamonaviy mijoz.
- `secrets` (Python built-in): Xavfsiz, taxmin qilib bo'lmaydigan tokenlar generatsiya qilish uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Backendda Token generatsiyasi:**
  - Foydalanuvchi profilida "Telegramni ulash" tugmasini bosganda ishlaydigan API yaratish.
  - Har bir foydalanuvchi uchun unikal, muddati cheklangan bir martalik token generatsiya qilish (`secrets.token_urlsafe(32)`).
  - Foydalanuvchiga Telegram bot havolasini qaytarish: `https://t.me/bizning_botimiz?start=<bir_martalik_token>`.
- [ ] **Backendda Ichki Xavfsiz Bog'lash Endpointi:**
  - Faqat Bot murojaat qila oladigan maxsus endpoint (masalan: `/api/v1/bot/link-telegram/`).
  - Xavfsizlik: Bot har bir so'rovda maxfiy sarlavha (masalan: `X-Bot-Api-Secret: your_secret_key`) yuborishi shart. Begonalar bu endpointga kira olmasligi kerak!
  - Ushbu endpoint berilgan tokenni tekshiradi, egasini topadi va uning `telegram_chat_id` maydoniga foydalanuvchining Telegram ID'sini yozib qo'yadi.
- [ ] **Aiogram 3 da Bot tuzilishi:**
  - `/start` komandasini qabul qilish. Agar komandada deep-link token kelsa (masalan: `/start abc123xyz`), bot tokenni olib Backend API'ga yuboradi.
  - Agar muvaffaqiyatli bog'lansa: foydalanuvchiga "Tabriklaymiz, profilingiz Evently tizimiga ulandi!" xabarini berish.
- [ ] **Botdagi foydali buyruqlar:**
  - `/my_events`: Foydalanuvchining yaqinlashib kelayotgan tadbirlarini backenddan so'rab olib, chiroyli ro'yxat qilib chiqarib berish.
  - `/help`: Botdan qanday foydalanish bo'yicha yo'riqnoma.

### 💡 Mentordan o'ylash uchun savollar:
1. Nima uchun foydalanuvchidan Telegramda telefon raqamini yoki emailini so'rashdan ko'ra Deep-link token orqali bog'lash xavfsizroq va qulayroq?
2. `BOT_API_SECRET` sirini nima uchun hech qachon GitHub'ga yuklamaslik va faqat `.env` da saqlash shart?

---

## 8-BOSQICH: Eslatmalar (Reminders) Tizimi va Avtomatlashtirish

> **Mentor eslatmasi:**  
> "Tadbirga 100 kishi yozildi, lekin yarmidan ko'pi esidan chiqarib kelmadi. Loyihamizning asosiy talablaridan biri — tadbirdan **24 soat oldin** barcha qatnashchilarga Telegram orqali eslatma yuborish.  
> Bu vazifani bajarish uchun har daqiqada butun bazani titkilash shart emas. Buning uchun Djangoda maxsus `Management Command` yozamiz va uni avtomatik rejalashtiruvchi (Cron) orqali ishga tushiramiz."

### 📚 Foydalaniladigan kutubxonalar:
- Django Core: `BaseCommand` (Custom CLI buyruqlari yaratish uchun).
- `django.utils.timezone`: Vaqt mintaqalarini to'g'ri solishtirish uchun.
- `httpx` yoki Telegram Bot API: Xabarlarni yuborish uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Takroriy xabar ketishini oldini olish (Idempotency):**
  - Eslatma bitta odamga bir necha marta ketib qolmasligi kerak!
  - `Registration` modeliga `reminder_sent = models.BooleanField(default=False)` maydoni yoki alohida bildirishnomalar jurnali (`NotificationLog`) qo'shish.
- [ ] **Custom Django Management Command yaratish:**
  - `apps/events/management/commands/send_reminders.py` faylini tashkil qilish.
  - Buyruq nomini shunday sozlashki, terminalda: `python manage.py send_reminders` deb chaqirilsin.
- [ ] **Eslatma yuborish algoritmi:**
  - Hozirgi vaqtdan boshlab keyingi 24 soat ichida (masalan, `now` dan `now + timedelta(hours=24)` oralig'ida) boshlanadigan tadbirlarni topish.
  - Ushbu tadbirlarga yozilgan, statusi `confirmed` bo'lgan, hali eslatma olmagan (`reminder_sent=False`) va Telegrami ulangan (`telegram_chat_id__isnull=False`) foydalanuvchilarni filtrlash.
  - Har bir foydalanuvchiga Telegram orqali chiroyli xabar yuborish: "Eslatma! Ertaga siz ro'yxatdan o'tgan '[Tadbir nomi]' bo'lib o'tadi. Manzil: ... Vaqti: ...".
  - Xabar muvaffaqiyatli yuborilgach, `reminder_sent = True` qilib saqlash.
- [ ] **Avtomatlashtirish (Cron / Scheduler):**
  - Serverda bu buyruqni har soatda yoki har 30 daqiqada avtomatik ishga tushirish uchun Linux Crontab yoki rejalashtiruvchi sozlamasini tayyorlash.

### 💡 Mentordan o'ylash uchun savollar:
1. Agar bir vaqtda 5 000 ta foydalanuvchiga xabar yuborish kerak bo'lsa, Telegram Bot API'ning cheklovlari (Rate limits: soniyasiga ~30 ta xabar) ga qanday moslashish kerak?
2. Nima uchun sana va vaqt bilan ishlaganda doimo `timezone.now()` ishlatish kerak va `datetime.now()` dan qochish lozim?

---

## 9-BOSQICH: Avtomatlashtirilgan Testlar (Testing & QA)

> **Mentor eslatmasi:**  
> "Test yozmaydigan dasturchi — xuddi ko'zini yumib mashina haydagan haydovchiga o'xshaydi. Ertaga loyihaga yangi bitta funksiya qo'shganingda, avval yozgan 5 ta funksiyang sinib qolmasligiga qanday kafolat berasan?  
> Testlar — bu sening xavfsizlik kamaring. Bu bosqichda biz Djangoning asosiy biznes qoidalari to'g'ri ishlayotganini avtomatik testlar bilan isbotlaymiz."

### 📚 Foydalaniladigan kutubxonalar:
- `pytest`: Zamonaviy, toza va tushunarli test runner.
- `pytest-django`: Pytest'ni Django bazasi, client va sozlamalari bilan integratsiya qilish uchun.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Muhitni sozlash:**
  - `pytest.ini` konfiguratsiya faylini yaratish va `DJANGO_SETTINGS_MODULE` ni ko'rsatish.
  - Sinovlar alohida izolyatsiyalangan test bazasida ishlashini ta'minlash (`db` fixture).
- [ ] **Majburiy Test Ssenariylari:**
  1. **Autentifikatsiya testi:** Yangi user ro'yxatdan o'ta oladimi? Login qilib JWT token ola biladimi? Noto'g'ri parol kiritilganda 401 xatosi qaytadimi?
  2. **Admin va User huquqlari testi:** Oddiy foydalanuvchi tadbir yaratishga urinib ko'rsa 403 Forbidden oladimi? Admin yaratganda 201 Created bo'ladimi?
  3. **Tadbir sanasi validatsiyasi:** O'tib ketgan sanaga tadbir yaratmoqchi bo'linganda 400 Bad Request qaytadimi?
  4. **Ro'yxatdan o'tish testi:** Bosh joy bor tadbirga muvaffaqiyatli yozilish mumkinmi?
  5. **Takroriy yozilishni taqiqlash testi:** Bir xil user bir xil tadbirga ikkinchi marta yozilmoqchi bo'lsa xato beradimi?
  6. **Joy to'lib qolishi (Capacity limit) testi:** Sig'imi 2 kishilik tadbirga 3-odam yozilmoqchi bo'lganda tizim xato qaytaradimi?
  7. **Bekor qilish testi:** Foydalanuvchi ro'yxatdan chiqqanda bo'sh joylar soni qayta tiklanadimi?
- [ ] **Testlarni ishga tushirish:**
  - Barcha testlar yashil (`PASSED`) bo'lishiga erishish.

### 💡 Mentordan o'ylash uchun savollar:
1. Unit test bilan Integration test o'rtasida qanday farq bor?
2. `APIClient` yordamida autentifikatsiyadan o'tgan foydalanuvchi nomidan so'rov yuborish uchun qaysi metoddan foydalaniladi (`force_authenticate` yoki header orqali)?

---

## 10-BOSQICH: Production Tayyorgarligi, Xavfsizlik va Deployment

> **Mentor eslatmasi:**  
> "Kod faqat sening kompyuteringda ishlashi yetarli emas — u butun dunyo uchun internetda ishlashi kerak!  
> Ko'pchilik loyihani serverga qo'yishda `DEBUG=True` qoldirib ketadi yoki maxfiy kalitlarini ochiq qoldiradi. Bu dahshatli xavfsizlik fojiasi. Oxirgi bosqichda biz loyihani professional tarzda deploy qilamiz."

### 📚 Foydalaniladigan asboblar va kutubxonalar:
- `gunicorn`: Django ilovalarini production muhitida ishlatuvchi WSGI HTTP server.
- `whitenoise`: Static fayllarni (Swagger UI dizayni, Admin CSS/JS) serverda engil va tez tarqatish uchun.
- Platformalar: Render, Railway yoki shaxsiy Ubuntu VPS.

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?
- [ ] **Xavfsizlik tekshiruvi (Production Checklist):**
  - Serverda `DEBUG=False` bo'lishi shart.
  - `ALLOWED_HOSTS` ga server domen nomlarini yoki IP manzilini yozish.
  - `SECRET_KEY` va barcha parollarni faqat serverning muhit o'zgaruvchilarida (Environment Variables) saqlash.
- [ ] **Statik fayllarni sozlash:**
  - `STATIC_ROOT` va `STATIC_URL` ni belgilash.
  - `whitenoise` middleware orqali statik fayllarni compress va cache qilib tarqatishni yo'lga qo'yish.
  - `python manage.py collectstatic` buyrug'i xatosiz ishlashini tekshirish.
- [ ] **Ishga tushirish skriptlari va konfiguratsiya:**
  - `Procfile` yoki `Dockerfile` yaratish.
  - Gunicorn orqali Djangoni ko'tarish buyrug'i: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
- [ ] **Deploymentni amalga oshirish:**
  - PostgreSQL bazasini bulutda ulash.
  - Migratsiyalarni serverda avtomatik yurgizish (`python manage.py migrate`).
  - Telegram botni alohida background worker sifatida ishga tushirish (masalan: `python bot/main.py`).
- [ ] **Swagger hujjatini tekshirish:**
  - Jonli domen bo'yicha Swagger ochilishi va barcha API'lar ishlab turganini tekshirish.

### 💡 Mentordan o'ylash uchun savollar:
1. `python manage.py check --deploy` buyrug'i nima uchun kerak va u qanday xavflarni ko'rsatib beradi?
2. Production'da nega `python manage.py runserver` ishlatish qat'iyan taqiqlanadi?

---

## 🎓 Mentordan Yakuniy Tavsiyalar va "Dasturchi Qoidalari"

1. **Git bilan madaniyatli ishlash:**
   - Har bir bosqich tugagach, aniq va mazmunli commit yozing (masalan: `feat: implement user registration with JWT`, `fix: prevent race condition on event registration`).
   - Hech qachon `.env`, `.venv`, yoki `__pycache__` papkalarini GitHub'ga commit qilmang!

2. **Xato chiqishidan qo'rqmang:**
   - Dasturchilikning 70% vaqti xatolarni o'qish (debugging) bilan o'tadi. Traceback'ni pastdan yuqoriga diqqat bilan o'qing, xato qaysi qatorda chiqqanini tushuning.

3. **Dokumentatsiyani do'st tuting:**
   - Tayyor kod qidirishdan oldin Django rasmiy qo'llanmasi (docs.djangoproject.com) va DRF qo'llanmasiga (django-rest-framework.org) qarang.

> **Keyingi qadam:**  
> Ushbu rejani qadamma-qadam bosib o'tishga tayyormisiz?  
> **1-BOSQICH** dan boshlaymiz! Har bir topshiriqni bajarib, natijasini menga aytib turing — men sizga yo'l ko'rsatib, yozgan kodingizni tahlil qilib beraman. Olg'a!
