# Evently — Professional Backend Dasturchi Uchun Yo'l Xaritasi (Mentor Guide)

> **Mentor so'zi:**  
> "Ukam / do'stim, ushbu qo'llanmada senga har bir bosqichda qaysi fayl nima vazifani bajarishi, aynan qayerga nima yozilishi va nima uchun yozilishi batafsil tushuntiriladi.  
> Dasturchilikda eng katta chalkashlik — qaysi kod qayerga yozilishini bilmaslikdan kelib chiqadi.  
> Esda tut: **`models.py`** — bu ma'lumotlar bazasi jadvallari, **`serializers.py`** — kelayotgan JSON ma'lumotlarni tekshirish (validatsiya) va tozalash, **`views.py`** — API so'rovlarini qabul qilib javob beruvchi miya, **`urls.py`** — marshrutlar yo'l ko'rsatkichi, **`permissions.py`** — xavfsizlik darvozasi.  
> Har bir topshiriq ostida uning fayli, vazifasi va izohi keltirilgan. Qani, boshladik!"

---

## 📌 Status Belgilari (O'zingiz belgilab boring)
- `[ ]` — Hali boshlanmagan
- `[/]` — Jarayonda
- `[x]` — Bajarildi, sinovdan o'tdi va git commit qilindi

---

## 🧰 Umumiy Texnologiyalar Steki va Kutubxonalar

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
| **drf-spectacular** | 0.27+ | Zamonaviy OpenAPI 3.0 sxemasi va chiroyli Swagger UI/Redoc yaratish. |
| **aiogram** | 3.4+ | Asinxron Telegram bot yaratish uchun eng mashhur Python kutubxona. |
| **httpx** | 0.27+ | Bot va Backend o'rtasida zamonaviy asinxron HTTP so'rovlar yuborish. |
| **pytest & pytest-django** | 8.0+ | Djangoning standart `TestCase`iga qaraganda ancha qulay va tezkor test tizimi. |

---

## 🧭 Loyihaning Bosqichma-bosqich Rejasi (Phases)

```
[Phase 1: Muhit, Baza va Custom User] (Bajarildi ✅)
                ⬇
[Phase 2: JWT Auth, Profil va Swagger] (Hozirgi Bosqich 🎯)
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
> "Django bilan ishlashda eng katta va tuzatib bo'lmas xato — standart `auth.User` bilan `migrate` qilib yuborishdir! Standart userda email majburiy emas va username talab qilinadi. Biz boshidanoq `AbstractUser` orqali Custom User yaratdik."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [x] **Virtual muhit va paketlarni o'rnatish:**
  - 📁 **Qaysi fayllar:** `pyproject.toml`, `.venv/`
  - 📝 **Nima qilinadi:** Terminalda `uv venv` orqali virtual muhit yaratiladi va `uv add django djangorestframework psycopg django-environ django-cors-headers drf-spectacular djangorestframework-simplejwt` o'rnatiladi.
  - 💡 **Nega kerak (Izoh):** Loyihaning barcha tashqi kutubxonalari kompyuterdagi global Python muhitiga aralashmasdan, aynan shu loyiha uchun izolyatsiya qilingan holda saqlanadi.

- [x] **Kataloglar arxitekturasi (Apps strukturasi):**
  - 📁 **Qaysi papka:** `apps/`, `apps/users/`
  - 📝 **Nima qilinadi:** Barcha Django ilovalarini loyiha ildizida emas, alohida `apps/` papkasi ichida jamlash (`apps.users`).
  - 💡 **Nega kerak (Izoh):** Kelajakda loyihada 10-15 ta ilova bo'lsa, fayllar chalkashib ketmasligi va arxitektura modulli (tartibli) bo'lishi uchun kerak.

- [x] **Konfiguratsiya va `.env` integratsiyasi:**
  - 📁 **Qaysi fayllarga:** `.env` va `config/settings.py`
  - 📝 **Nima yoziladi:** `.env` da `SECRET_KEY`, `DEBUG`, `DATABASE_URL` yoziladi. `config/settings.py` da `environ.Env()` orqali ular o'qib olinadi.
  - 💡 **Nega kerak (Izoh):** Maxfiy kalitlar, parollar va baza ma'lumotlari GitHub'ga ochiq chiqib ketmasligi va turli muhitlarda (local vs production) oson o'zgartirilishi uchun (12-Factor tamoyili).

- [x] **Custom User modeli:**
  - 📁 **Qaysi faylga:** `apps/users/models.py`
  - 📝 **Nima yoziladi:** `User(AbstractUser)` modeli yaratiladi: `username = None`, `email = models.EmailField(unique=True)`, `role` (Admin/User), `phone_number`, `telegram_chat_id`, `telegram_link_token`. Shuningdek, email orqali user yaratuvchi `UserManager(BaseUserManager)` yoziladi.
  - 💡 **Nega kerak (Izoh):** PostgreSQL ma'lumotlar bazasida foydalanuvchilar jadvali (`users_user`) yaratiladi. Foydalanuvchi tizimga username bilan emas, email bilan kirishi uchun aynan shu model poydevor hisoblanadi.

- [x] **`AUTH_USER_MODEL` sozlamasi:**
  - 📁 **Qaysi faylga:** `config/settings.py`
  - 📝 **Nima yoziladi:** `AUTH_USER_MODEL = 'users.User'`
  - 💡 **Nega kerak (Izoh):** Djangoga: "Eski standart User modelingni unut, bundan buyon `apps/users/models.py` dagi biz yozgan User modelini asosiy foydalanuvchi deb bilgin" deb uqtirish uchun.

- [x] **Admin panel:**
  - 📁 **Qaysi faylga:** `apps/users/admin.py`
  - 📝 **Nima yoziladi:** `UserAdmin` klassi orqali yangi maydonlar (`role`, `phone_number`, `telegram_chat_id`) admin panelda ro'yxatga olinadi.
  - 💡 **Nega kerak (Izoh):** Brauzer orqali `/admin/` paneliga kirilganda yangi qo'shilgan ustunlarni ko'rish va tahrirlash imkoniyati bo'lishi uchun.

- [x] **Birinchi migratsiya va superuser:**
  - 📁 **Qaysi fayllar:** `apps/users/migrations/0001_initial.py`, PostgreSQL bazasi
  - 📝 **Nima qilinadi:** `python manage.py makemigrations` va `python manage.py migrate`. So'ngra `createsuperuser` bilan admin yaratiladi.
  - 💡 **Nega kerak (Izoh):** Python kodida yozilgan modellar PostgreSQL ma'lumotlar bazasida haqiqiy jadvallar (SQL CREATE TABLE) ko'rinishida hosil bo'lishi uchun.

---

## 2-BOSQICH: Autentifikatsiya (JWT), Profil va Swagger (API Hujjatlari)

> **Mentor eslatmasi:**  
> "Biz REST API quryapmiz. Bu degani server sessiya (cookie session) saqlamaydi — u **Stateless** bo'lishi kerak. SimpleJWT yordamida foydalanuvchi login qilganda `access token` (har bir so'rovga qo'shib yuboriladigan kalit) va `refresh token` (yangi access olish uchun kalit) qaytaramiz."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **DRF va SimpleJWT global sozlamalari:**
  - 📁 **Qaysi faylga:** `config/settings.py`
  - 📝 **Nima yoziladi:**
    ```python
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    }
    ```
  - 💡 **Nega kerak (Izoh):** Django REST Framework barcha kelayotgan so'rovlarni avtomatik ravishda JWT token orqali tekshirishini va tokenlarning qancha vaqt yashashini belgilash uchun.

- [ ] **Foydalanuvchi ro'yxatdan o'tishi (Register Serializer):**
  - 📁 **Qaysi faylga:** `apps/users/serializers.py`
  - 📝 **Nima yoziladi:** `UserRegisterSerializer` klassi:
    - Maydonlar: `email`, `first_name`, `last_name`, `phone_number`, `password`, `password_confirm`.
    - `validate()` metodi: ikkala parol bir xilligini va xavfsizlik talablariga mosligini tekshiradi.
    - `create()` metodi: `User.objects.create_user()` orqali parolni hashlab yangi user yaratadi. Parollar `write_only=True` qilinadi.
  - 💡 **Nega kerak (Izoh):** Foydalanuvchi yuborgan xom JSON ma'lumotlarini qabul qilib, ularning to'g'riligini tekshirish (validatsiya) va bazaga xavfsiz saqlash uchun.

- [ ] **Ro'yxatdan o'tish ko'rinishi (Register View):**
  - 📁 **Qaysi faylga:** `apps/users/views.py`
  - 📝 **Nima yoziladi:** `RegisterView(generics.CreateAPIView)`:
    - `serializer_class = UserRegisterSerializer`
    - `permission_classes = [AllowAny]`
  - 💡 **Nega kerak (Izoh):** Frontend yoki mijozdan kelgan HTTP `POST` so'rovini kutib olib, serializer orqali bazada yangi foydalanuvchi yaratadi va `201 Created` javobini qaytaradi.

- [ ] **Login va Token olish (Login & Refresh):**
  - 📁 **Qaysi fayllarga:** `apps/users/serializers.py` va `apps/users/views.py`
  - 📝 **Nima yoziladi:** `CustomTokenObtainPairSerializer` (agar tokenga foydalanuvchi roli yoki ismi qo'shilishi kerak bo'lsa) hamda SimpleJWT ning `TokenObtainPairView` va `TokenRefreshView` lari.
  - 💡 **Nega kerak (Izoh):** Foydalanuvchi o'zining `email` va `password` ini yuborganda, tizim unga tizimga kirish huquqini beruvchi `access` va `refresh` tokenlarni berishi uchun.

- [ ] **Profil ko'rish va tahrirlash (`/auth/me/`):**
  - 📁 **Qaysi fayllarga:**
    1. `apps/users/serializers.py` — `UserProfileSerializer`: foydalanuvchining shaxsiy ma'lumotlarini JSON formatga o'giradi va yangilash imkonini beradi.
    2. `apps/users/views.py` — `UserProfileView(generics.RetrieveUpdateAPIView)`: `permission_classes = [IsAuthenticated]`, `get_object()` metodi orqali aynan so'rov yuborgan `self.request.user` ni qaytaradi.
  - 💡 **Nega kerak (Izoh):** Tizimga kirgan foydalanuvchi o'z ma'lumotlarini (ism, familiya, telefon) ko'rishi va tahrirlashi uchun. Begonalar bu ma'lumotlarni ko'ra olmaydi.

- [ ] **Foydalanuvchi URL marshrutlari:**
  - 📁 **Qaysi faylga:** `apps/users/urls.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    - `path('register/', RegisterView.as_view(), name='register')`
    - `path('login/', TokenObtainPairView.as_view(), name='login')`
    - `path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')`
    - `path('me/', UserProfileView.as_view(), name='profile')`
  - 💡 **Nega kerak (Izoh):** API endpointlarini (manzillarini) mos view'larga bog'lash uchun.

- [ ] **Swagger UI va Redoc integratsiyasi:**
  - 📁 **Qaysi fayllarga:** `config/settings.py` va `config/urls.py`
  - 📝 **Nima yoziladi:**
    - `INSTALLED_APPS` ga `'drf_spectacular'` qo'shish.
    - `config/urls.py` ga `SpectacularAPIView`, `SpectacularSwaggerView.as_view(url_name='schema')` va `SpectacularRedocView.as_view(url_name='schema')` ni ulash.
    - `config/urls.py` ga `path('api/v1/auth/', include('apps.users.urls'))` ni ulash.
  - 💡 **Nega kerak (Izoh):** Brauzer orqali `/api/docs/` manziliga kirib, yaratilgan barcha API'larni qulay interfeysda ko'rish, "Authorize" tugmasi orqali token kiritib, API'larni test qilish uchun.

---

## 3-BOSQICH: Tadbirlar (Events) Moduli, CRUD va Maxsus Huquqlar (Permissions)

> **Mentor eslatmasi:**  
> "Ushbu bosqichda asosiy biznes obyektimiz — Tadbirlar (Events) yaratiladi. Bu yerda kim nima qila olishi muhim: oddiy foydalanuvchi tadbirlarni faqat ko'ra oladi (`GET`), lekin yangi tadbir yaratish, uni o'zgartirish yoki o'chirish faqat **Admin** larga ruxsat etiladi."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Yangi ilova yaratish (`apps/events`):**
  - 📁 **Qaysi papka:** `apps/events/`
  - 📝 **Nima qilinadi:** Terminalda: `python manage.py startapp events apps/events` va `config/settings.py` dagi `INSTALLED_APPS` ga `'apps.events'` ni kiritish.
  - 💡 **Nega kerak (Izoh):** Tadbirlar bilan bog'liq barcha mantiqni o'zida saqlovchi mustaqil modul yaratish uchun.

- [ ] **Event modeli:**
  - 📁 **Qaysi faylga:** `apps/events/models.py`
  - 📝 **Nima yoziladi:** `Event` klassi:
    - `title = models.CharField(max_length=255)`
    - `description = models.TextField()`
    - `date = models.DateTimeField()` (tadbirlar o'tkazilish sanasi)
    - `location = models.CharField(max_length=255)`
    - `capacity = models.PositiveIntegerField()` (maksimal sig'im)
    - `status = models.CharField(choices=EventStatus.choices, default=EventStatus.OPEN)` (open, full, cancelled, completed)
    - `created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')`
    - `created_at = models.DateTimeField(auto_now_add=True)`
    - `updated_at = models.DateTimeField(auto_now=True)`
  - 💡 **Nega kerak (Izoh):** PostgreSQL bazasida tadbirlar saqlanadigan `events_event` jadvalini yaratish uchun.

- [ ] **Tadbir sanasi va sig'imi validatsiyasi:**
  - 📁 **Qaysi faylga:** `apps/events/serializers.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:** `EventSerializer(serializers.ModelSerializer)`:
    - `validate_date()`: Tadbir sanasi hozirgi vaqtdan kelajakda bo'lishini tekshiradi (`value > timezone.now()`). O'tib ketgan sana kiritilsa xato beradi.
    - `validate_capacity()`: Sig'im kamida 1 bo'lishini tekshiradi.
  - 💡 **Nega kerak (Izoh):** O'tmishdagi sanaga tadbir yaratilishining oldini oladi va xato kiritilgan ma'lumotlarni bazaga yetib bormasdan to'xtatadi.

- [ ] **Maxsus Huquq (Custom Permission):**
  - 📁 **Qaysi faylga:** `apps/events/permissions.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:** `IsAdminOrReadOnly(permissions.BasePermission)` klassi:
    - `has_permission()` metodi: Agar so'rov `GET`, `HEAD`, `OPTIONS` (xavfsiz amallar) bo'lsa — barchaga ruxsat beradi.
    - Agar `POST`, `PUT`, `PATCH`, `DELETE` bo'lsa — faqat `request.user.role == 'admin'` yoki `is_staff=True` bo'lgan foydalanuvchilarga ruxsat beradi.
  - 💡 **Nega kerak (Izoh):** Oddiy qatnashchilar tadbir yaratib yoki boshqa tadbirlarni o'chirib yubormasligi uchun API darajasidagi xavfsizlik filtri.

- [ ] **Events CRUD ko'rinishi (ViewSet):**
  - 📁 **Qaysi faylga:** `apps/events/views.py`
  - 📝 **Nima yoziladi:** `EventViewSet(viewsets.ModelViewSet)`:
    - `queryset = Event.objects.all()`
    - `serializer_class = EventSerializer`
    - `permission_classes = [IsAdminOrReadOnly]`
    - `perform_create(serializer)`: Tadbir yaratilayotganda `created_by=self.request.user` qilib avtomatik tashkilotchini biriktiradi.
  - 💡 **Nega kerak (Izoh):** Bitta klass orqali ro'yxatni olish (`GET /events/`), bitta tadbirni ko'rish (`GET /events/{id}/`), yangi yaratish (`POST`), o'zgartirish (`PUT/PATCH`) va o'chirish (`DELETE`) amallarini ta'minlash uchun.

- [ ] **Events URL marshrutlari:**
  - 📁 **Qaysi fayllarga:** `apps/events/urls.py` [YANGI FAYL] va `config/urls.py`
  - 📝 **Nima yoziladi:** `DefaultRouter` yaratib, unga `router.register('events', EventViewSet)` ni ro'yxatdan o'tkazish. `config/urls.py` da `path('api/v1/', include('apps.events.urls'))` ulash.
  - 💡 **Nega kerak (Izoh):** Barcha CRUD marshrutlarini bitta router orqali avtomatik hosil qilish uchun.

- [ ] **Migratsiyalarni bajarish:**
  - 📁 **Qaysi papka:** `apps/events/migrations/`
  - 📝 **Nima qilinadi:** `python manage.py makemigrations events` va `python manage.py migrate`.
  - 💡 **Nega kerak (Izoh):** Yangi `Event` modelini PostgreSQL ma'lumotlar bazasida jadval sifatida yaratish uchun.

---

## 4-BOSQICH: Qidiruv, Filtrlash, Pagination va Query Optimizatsiyasi (N+1 Muammosi)

> **Mentor eslatmasi:**  
> "Bazada 10 000 ta tadbir bo'lsa, ularni birdaniga olib kelish serverni o'ldiradi. Shuning uchun sahifalash (Pagination) kerak. Shuningdek, har bir tadbir bilan uning tashkilotchisini tortib olishda N+1 ta so'rov ketmasligi uchun `select_related` ishlatamiz."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Pagination sozlamalari (Sahifalash):**
  - 📁 **Qaysi faylga:** `config/settings.py` (yoki `apps/common/pagination.py`)
  - 📝 **Nima yoziladi:**
    ```python
    REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] = 'rest_framework.pagination.PageNumberPagination'
    REST_FRAMEWORK['PAGE_SIZE'] = 10
    ```
  - 💡 **Nega kerak (Izoh):** API har bir chaqirilganda maksimal 10 ta tadbir qaytarishi, qolganlarini `page=2`, `page=3` deb sahifalab olish imkonini berishi uchun.

- [ ] **Filter klassini yaratish:**
  - 📁 **Qaysi faylga:** `apps/events/filters.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:** `EventFilter(django_filters.FilterSet)`:
    - Sana oralig'i: `date_from = DateTimeFilter(field_name='date', lookup_expr='gte')`, `date_to = DateTimeFilter(field_name='date', lookup_expr='lte')`
    - Status: `status = ChoiceFilter(choices=EventStatus.choices)`
  - 💡 **Nega kerak (Izoh):** Foydalanuvchilar `/api/v1/events/?status=open&date_from=2026-12-01` ko'rinishida parametrlarga qarab saralashi uchun.

- [ ] **Qidiruv, tartiblash va filterni View'ga ulash:**
  - 📁 **Qaysi faylga:** `apps/events/views.py`
  - 📝 **Nima yoziladi:**
    - `filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]`
    - `filterset_class = EventFilter`
    - `search_fields = ['title', 'description']` (nomi va matni bo'yicha qidiruv)
    - `ordering_fields = ['date', 'created_at']`
  - 💡 **Nega kerak (Izoh):** DRF view'da bir vaqtning o'zida qidiruv (`?search=python`), tartiblash (`?ordering=date`) va filtrlarni ishga tushirish uchun.

- [ ] **SQL Query Optimizatsiyasi (N+1 ni yo'qotish va bo'sh joylarni sanash):**
  - 📁 **Qaysi faylga:** `apps/events/views.py`
  - 📝 **Nima yoziladi:** `get_queryset()` metodida:
    ```python
    return Event.objects.select_related('created_by') \
        .annotate(registered_count=Count('registrations', filter=Q(registrations__status='confirmed')))
    ```
  - 💡 **Nega kerak (Izoh):** `select_related('created_by')` orqali tashkilotchi ma'lumotlari bitta SQL JOIN bilan olinadi (100 ta alohida so'rov ketmaydi). `annotate` orqali esa ro'yxatdan o'tganlar soni Python siklida emas, to'g'ridan-to'g'ri PostgreSQL bazasi darajasida tezkor hisoblanadi.

- [ ] **Bo'sh joylarni Serializer'da ko'rsatish:**
  - 📁 **Qaysi faylga:** `apps/events/serializers.py`
  - 📝 **Nima yoziladi:** Serializer'ga `registered_count` va `available_seats = serializers.SerializerMethodField()` qo'shiladi:
    ```python
    def get_available_seats(self, obj):
        count = getattr(obj, 'registered_count', 0)
        return max(0, obj.capacity - count)
    ```
  - 💡 **Nega kerak (Izoh):** Frontend qatnashchiga necha dona bo'sh o'rin qolganini real vaqtda ko'rsatib turishi uchun.

---

## 5-BOSQICH: Ro'yxatdan o'tish (Registration) Tizimi va Race Condition Muammosi

> **Mentor eslatmasi:**  
> "Tadbirda atigi 1 ta joy qolganda 10 kishi birdaniga ariza bersa, oddiy tekshiruv ish bermaydi va 1 ta joyga 10 kishi yozilib ketadi (Race Condition). Buni yechish uchun biz `transaction.atomic()` va PostgreSQL darajasida qatorni qulflash — `select_for_update()` dan foydalanamiz."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Yangi ilova yaratish (`apps/registrations`):**
  - 📁 **Qaysi papka:** `apps/registrations/`
  - 📝 **Nima qilinadi:** Terminalda: `python manage.py startapp registrations apps/registrations` va `settings.py` ga qo'shish.
  - 💡 **Nega kerak (Izoh):** Ro'yxatdan o'tishlar va chiptalar tarixini alohida toza modulda yuritish uchun.

- [ ] **Registration modeli va Constraint:**
  - 📁 **Qaysi faylga:** `apps/registrations/models.py`
  - 📝 **Nima yoziladi:** `Registration` modeli:
    - `user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')`
    - `event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')`
    - `status = models.CharField(choices=RegistrationStatus.choices, default=RegistrationStatus.CONFIRMED)` (confirmed, cancelled)
    - `registered_at = models.DateTimeField(auto_now_add=True)`
    - `reminder_sent = models.BooleanField(default=False)`
    - Meta qismida: `models.UniqueConstraint(fields=['user', 'event'], name='unique_active_user_event_registration')`
  - 💡 **Nega kerak (Izoh):** PostgreSQL bazasida qatnashuvchilar jadvali yaratiladi va ma'lumotlar bazasi darajasida bitta odam bitta tadbirga bir vaqtda faqat bir marta yozilishi kafolatlanadi.

- [ ] **Race Condition'ni yenguvchi Biznes Servis (Service Layer):**
  - 📁 **Qaysi faylga:** `apps/registrations/services.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:** `register_user_to_event(user, event_id)` funksiyasi:
    - `@transaction.atomic` dekoratori orqali tranzaksiyaga olinadi.
    - `event = Event.objects.select_for_update().get(id=event_id)` orqali bazadagi tadbir qatori qulflanadi.
    - Joriy aktiv ro'yxatdan o'tganlar soni sanaladi: `confirmed_count = event.registrations.filter(status='confirmed').count()`.
    - Agar `confirmed_count >= event.capacity` bo'lsa: `event.status = 'full'`, saqlanadi va `ValidationError("Bo'sh joy qolmagan!")` tashlanadi.
    - Joy bo'lsa: `Registration.objects.create(user=user, event=event)` qilinadi.
  - 💡 **Nega kerak (Izoh):** Bir soniyada 100 ta so'rov kelsa ham, PostgreSQL ularni birma-bir navbatga qo'yadi. Birinchi odam o'rinni egallagach, keyingilari 'joy qolmagan' xatosini oladi. Ortiqcha odam yozilishi mutlaqo imkonsiz bo'ladi.

- [ ] **Registration Serializer va View:**
  - 📁 **Qaysi fayllarga:** `apps/registrations/serializers.py` va `apps/registrations/views.py`
  - 📝 **Nima yoziladi:**
    - `RegistrationCreateView(APIView)`: `permission_classes = [IsAuthenticated]`. `POST /api/v1/events/{id}/register/` so'rovida `register_user_to_event` servis funksiyasini chaqiradi.
  - 💡 **Nega kerak (Izoh):** API orqali autentifikatsiyadan o'tgan foydalanuvchilarning so'rovlarini qabul qilib, ularni servisga uzatish uchun.

- [ ] **Migratsiyalarni bajarish:**
  - 📁 **Qaysi papka:** `apps/registrations/migrations/`
  - 📝 **Nima qilinadi:** `python manage.py makemigrations registrations` va `python manage.py migrate`.
  - 💡 **Nega kerak (Izoh):** Bazada `registrations_registration` jadvali va unikal indekslarni hosil qilish uchun.

---

## 6-BOSQICH: Tadbirdan Chiqish, Shaxsiy Ro'yxatlar va Tadbirni Yopish

> **Mentor eslatmasi:**  
> "Odamlar rejalari o'zgarganda tadbirdan chiqib keta olishi kerak. Lekin bazadan butunlay o'chirib yuborish (Hard delete) tavsiya etilmaydi — statusni `cancelled` ga o'tkazish (Soft delete) orqali tarixni saqlaymiz va bo'shagan o'rinni darhol qayta ochamiz."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Tadbirdan chiqish (Cancel Registration API):**
  - 📁 **Qaysi fayllarga:** `apps/registrations/services.py` va `apps/registrations/views.py`
  - 📝 **Nima yoziladi:**
    - Servisda: `cancel_registration(user, registration_id)` funksiyasi. Ariza egasi ekanligini tekshiradi, tadbir sanasi o'tib ketmagan bo'lishini tekshiradi.
    - Statusni `cancelled` ga o'tkazadi.
    - Agar tadbir `status == 'full'` bo'lib turgan bo'lsa, o'rin bo'shagani sababli uni yana qayta `status = 'open'` holatiga o'tkazadi.
    - View'da: `POST /api/v1/registrations/{id}/cancel/` endpointi.
  - 💡 **Nega kerak (Izoh):** Qatnashchi bormoqchi bo'lmasa joyini bo'shatishi va boshqa odamlar yana ro'yxatdan o'tishi imkoniyati paydo bo'lishi uchun.

- [ ] **Mening arizalarim ro'yxati (`/registrations/my/`):**
  - 📁 **Qaysi fayllarga:** `apps/registrations/views.py` va `apps/registrations/serializers.py`
  - 📝 **Nima yoziladi:** `MyRegistrationsListView(generics.ListAPIView)`:
    - `permission_classes = [IsAuthenticated]`
    - `get_queryset()`: Faqat `request.user` ning arizalarini (`Registration.objects.filter(user=request.user)`) qaytaradi.
    - Serializer ichida tadbirning barcha ma'lumotlari (`EventSerializer`) birga ko'rsatiladi.
  - 💡 **Nega kerak (Izoh):** Har bir foydalanuvchi faqat o'zi qatnashayotgan tadbirlar chiptalarini ko'rishi uchun.

- [ ] **Admin tomonidan tadbirni muddatidan oldin yopish:**
  - 📁 **Qaysi faylga:** `apps/events/views.py`
  - 📝 **Nima yoziladi:** `EventViewSet` ga `@action(detail=True, methods=['post'], permission_classes=[IsAdminUserRole])` qo'shish (`/api/v1/events/{id}/close/`):
    - Tadbir statusini `cancelled` yoki `completed` ga o'zgartiradi.
  - 💡 **Nega kerak (Izoh):** Tashkilotchi tadbirni bekor qilganda yoki to'xtatganda unga boshqa hech kim yozila olmasligini ta'minlash uchun.

---

## 7-BOSQICH: Telegram Bot Integratsiyasi va Hisobni Bog'lash (Deep-Linking)

> **Mentor eslatmasi:**  
> "Telegram bot — bu Django ichida emas, alohida mustaqil ishlovchi asinxron mikroxizmat. U bazaga to'g'ridan-to'g'ri kirmaydi, balki biz yaratgan REST API bilan `httpx` orqali aloqa qiladi. Saytdagi akkauntni botga bog'lash esa xavfsiz bir martalik Deep-link token orqali bajariladi."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Backendda bir martalik bog'lash tokeni yaratish:**
  - 📁 **Qaysi fayllarga:** `apps/users/views.py` va `apps/users/urls.py`
  - 📝 **Nima yoziladi:** `TelegramLinkGenerateView(APIView)`:
    - `permission_classes = [IsAuthenticated]`
    - `token = secrets.token_urlsafe(32)` generatsiya qilib, foydalanuvchining `telegram_link_token` maydoniga yozadi.
    - Foydalanuvchiga bot havolasini qaytaradi: `https://t.me/bizning_botimiz?start={token}`.
  - 💡 **Nega kerak (Izoh):** Foydalanuvchi saytdagi tugmani bosganda uning akkauntini botga aniq va begonalarsiz bog'laydigan xavfsiz havola berish uchun.

- [ ] **Backendda Bot uchun Maxfiy Webhook Endpointi:**
  - 📁 **Qaysi fayllarga:** `apps/users/views.py` va `apps/users/urls.py`
  - 📝 **Nima yoziladi:** `TelegramConnectView(APIView)`:
    - Xavfsizlik: So'rov header'ida `X-Bot-Api-Secret` tekshiriladi (agar kalit to'g'ri bo'lmasa `403 Forbidden`).
    - Body'dan `token` va `telegram_chat_id` olinadi.
    - Berilgan token bo'yicha foydalanuvchi topiladi, uning `telegram_chat_id` siga yoziladi va `telegram_link_token = None` qilinadi (token kuyadi).
  - 💡 **Nega kerak (Izoh):** Bot foydalanuvchining telegram ID raqamini Django ma'lumotlar bazasidagi User jadvaliga yozib qo'yishi uchun.

- [ ] **Aiogram 3 da Telegram Bot loyihasini qurish:**
  - 📁 **Qaysi papka/fayllarga:** `bot/main.py`, `bot/config.py`, `bot/handlers/start.py` [YANGI PAPKA VA FAYLLAR]
  - 📝 **Nima yoziladi:**
    - `bot/main.py` — `Bot`, `Dispatcher` va polling'ni ishga tushiruvchi asinxron `async def main()`.
    - `/start <token>` handler'i: kelgan deep-link tokenni olib, Backendning `/api/v1/auth/telegram/connect/` endpointiga `httpx.AsyncClient` orqali POST so'rovi yuboradi.
    - Muvaffaqiyatli bo'lsa: "Profilingiz Evently tizimiga muvaffaqiyatli ulandi!" deb javob beradi.
  - 💡 **Nega kerak (Izoh):** Foydalanuvchilar Telegram orqali xabar olishlari va tadbirlarini kuzatib borishlari uchun interfeys yaratish.

- [ ] **Botdagi foydali buyruqlar:**
  - 📁 **Qaysi faylga:** `bot/handlers/events.py`
  - 📝 **Nima yoziladi:**
    - `/my_events` komandasi: backenddan ushbu `telegram_chat_id` ga tegishli arizalarni so'rab olib, chiroyli ro'yxat qilib chiqarib berish.
  - 💡 **Nega kerak (Izoh):** Foydalanuvchi saytga kirmasdan ham Telegram orqali o'z chiptalari va tadbirlarini ko'ra olishi uchun.

---

## 8-BOSQICH: Eslatmalar (Reminders) Tizimi va Avtomatlashtirish

> **Mentor eslatmasi:**  
> "Tadbirdan 24 soat oldin barcha qatnashchilarga eslatma yuborish kerak. Buni amalga oshirish uchun Djangoda maxsus `Management Command` yozamiz. U terminaldan yoki Linux Crontab orqali avtomatik chaqiriladi."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Eslatma buyrug'i fayl strukturasi:**
  - 📁 **Qaysi papka/faylga:** `apps/events/management/commands/send_reminders.py` [YANGI FAYL]
  - 📝 **Nima qilinadi:** Djangoda buyruqlar ishlashi uchun `management/` va `management/commands/` papkalarini yaratib ichiga bo'sh `__init__.py` qo'yish.
  - 💡 **Nega kerak (Izoh):** Djangoning `python manage.py <buyruq_nomi>` tizimi aynan shu katalog ichidagi fayllarni qidiradi.

- [ ] **Eslatma yuborish mantiqi (Command logic):**
  - 📁 **Qaysi faylga:** `apps/events/management/commands/send_reminders.py`
  - 📝 **Nima yoziladi:** `Command(BaseCommand)` klassi:
    - Hozirgi vaqt va 24 soatlik oraliqni hisoblash: `now = timezone.now()`, `target_time = now + timedelta(hours=24)`.
    - 24 soat ichida boshlanadigan tadbirlarga yozilgan, statusi `confirmed`, eslatma hali bormagan (`reminder_sent=False`) va `telegram_chat_id` si bor arizalarni filtrlash:
      ```python
      registrations = Registration.objects.filter(
          status='confirmed',
          reminder_sent=False,
          event__date__range=(now, target_time),
          user__telegram_chat_id__isnull=False
      ).select_related('user', 'event')
      ```
    - Telegram Bot API orqali xabar yuborish va `registration.reminder_sent = True` qilib saqlash.
  - 💡 **Nega kerak (Izoh):** Tadbir boshlanishiga 1 kun qolganda qatnashchilarga Telegram orqali avtomatik eslatma jo'natish va bitta odamga bir necha bor xabar bormasligini ta'minlash uchun.

- [ ] **Buyruqni sinab ko'rish:**
  - 📁 **Qayerda:** Terminal
  - 📝 **Nima qilinadi:** `python manage.py send_reminders` deb chaqirish.
  - 💡 **Nega kerak (Izoh):** Serverda cron rejalashtiruvchiga qo'yishdan oldin komanda xatosiz ishlayotganiga ishonch hosil qilish uchun.

---

## 9-BOSQICH: Avtomatlashtirilgan Testlar (Testing & QA)

> **Mentor eslatmasi:**  
> "Avtomatlashtirilgan testlar — backendchining xavfsizlik kamari. Yangi funksiya qo'shganingizda eskilari sinib qolmasligini kafolatlash uchun asosiy biznes ssenariylarini `pytest` bilan tekshiramiz."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Pytest sozlamalari:**
  - 📁 **Qaysi faylga:** `pytest.ini` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    ```ini
    [pytest]
    DJANGO_SETTINGS_MODULE = config.settings
    python_files = tests.py test_*.py *_tests.py
    ```
  - 💡 **Nega kerak (Izoh):** Pytest kutubxonasi qaysi Django sozlamalaridan foydalanishni va qaysi fayllar test ekanligini bilishi uchun.

- [ ] **Autentifikatsiya testlari:**
  - 📁 **Qaysi faylga:** `tests/test_auth.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    - Ro'yxatdan o'tish testi (`status_code == 201`).
    - Parollar mos kelmaganda `400 Bad Request` qaytishi.
    - Login qilib JWT access va refresh token olish testi (`status_code == 200`).
  - 💡 **Nega kerak (Izoh):** Foydalanuvchilar kirish tizimi hech qachon nosozlikka uchramasligini tekshirish uchun.

- [ ] **Tadbirlar va Ruxsatlar testi:**
  - 📁 **Qaysi faylga:** `tests/test_events.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    - Oddiy foydalanuvchi tadbir yaratmoqchi bo'lsa `403 Forbidden` olishi testi.
    - Admin yaratganda `201 Created` bo'lishi testi.
    - O'tib ketgan sanaga tadbir yaratib bo'lmasligi testi.
  - 💡 **Nega kerak (Izoh):** Rollar (admin vs oddiy user) va sanalar to'g'ri ishlayotganini isbotlash uchun.

- [ ] **Ro'yxatdan o'tish va Sig'im limiti testi:**
  - 📁 **Qaysi faylga:** `tests/test_registrations.py` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    - Sig'imi 2 kishilik tadbirga 3-foydalanuvchi yozila olmasligi (`400 Bad Request`).
    - Bir xil odam bir tadbirga ikki marta yozila olmasligi.
    - Ariza bekor qilinganda joy qayta ochilishi testi.
  - 💡 **Nega kerak (Izoh):** Asosiy biznes logikamiz — sig'im chegarasi va takroriy yozilishni taqiqlash to'g'ri ishlayotganini tekshirish uchun.

- [ ] **Testlarni ishga tushirish:**
  - 📁 **Qayerda:** Terminal
  - 📝 **Nima qilinadi:** `uv run pytest -v`
  - 💡 **Nega kerak (Izoh):** Barcha testlar yashil (`PASSED`) ekanligini ko'rish uchun.

---

## 10-BOSQICH: Production Tayyorgarligi, Xavfsizlik va Deployment

> **Mentor eslatmasi:**  
> "Oxirgi bosqich — loyihani internet tarmog'iga, butun dunyo foydalanishi uchun jonli serverga (VPS, Render yoki Railway) joylashtirish. Bu yerda xavfsizlik (`DEBUG=False`) va statik fayllar (`whitenoise`) eng muhim rol o'ynaydi."

### 🎯 Bu bosqichda nima ishlar qilinishi kerak?

- [ ] **Xavfsizlik va Statik fayllar sozlamalari:**
  - 📁 **Qaysi faylga:** `config/settings.py`
  - 📝 **Nima yoziladi:**
    - `MIDDLEWARE` ga `'whitenoise.middleware.WhiteNoiseMiddleware'` qo'shish.
    - `STATIC_ROOT = BASE_DIR / 'staticfiles'`
    - `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
  - 💡 **Nega kerak (Izoh):** Swagger UI dizayni va Django Admin paneli CSS/JS fayllari alohida Nginx'siz ham Python serverida tezkor tarqatilishi uchun.

- [ ] **WSGI Production Server buyruqlari:**
  - 📁 **Qaysi faylga:** `Procfile` [YANGI FAYL]
  - 📝 **Nima yoziladi:**
    ```
    web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
    worker: python -m bot.main
    ```
  - 💡 **Nega kerak (Izoh):** Bulutli serverlar (masalan Render, Railway) Django veb-serverini va Telegram botni avtomatik ravishda fonda qanday ishga tushirishni bilishi uchun.

- [ ] **Production deployment tekshiruvi:**
  - 📁 **Qayerda:** Terminal
  - 📝 **Nima qilinadi:** `python manage.py check --deploy` va `python manage.py collectstatic`.
  - 💡 **Nega kerak (Izoh):** Xavfsizlikda ochiq qolgan teshiklar yo'qligini va statik fayllar yig'ilishini tekshirish uchun.

---

## 🎓 Mentordan Yakuniy Tavsiyalar va "Dasturchi Qoidalari"

1. **Fayllar chegarasini buzmang:**
   - Hech qachon `views.py` ichida og'ir SQL so'rovlar yoki xom hisob-kitoblar qilmang — ularni `models.py` yoki `services.py` ga olib chiqing.
   - Hech qachon `serializers.py` ichida HTTP status kodlar yoki response qaytarmang — uning ishi faqat tekshirish (validatsiya) va tozalashdir.

2. **Git commit madaniyati:**
   - Har bir topshiriqni tugatgach, qaysi fayllarni o'zgartirganingizni yozib commit qiling:
     - `feat(auth): add register serializer and view`
     - `feat(events): implement event model and custom permission`

> **Keyingi qadam:**  
> 1-bosqich yakunlangan! Endi **2-BOSQICH: Autentifikatsiya (JWT), Profil va Swagger** ga kirishamiz.  
> Tayyor bo'lsangiz, birinchi topshiriq: `config/settings.py` da SimpleJWT va Swagger sozlamalarini ulaymiz!
