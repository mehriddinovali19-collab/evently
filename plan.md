# Evently — Loyihani amalga oshirish rejasi va Kodlar Qo'llanmasi (Plan & Code Guide)

> **Sizning rolingiz:** Backend Dasturchi (kodlarni o'zingiz yozasiz, tahlil qilasiz va ishga tushirasiz).  
> **Mening rolim:** Sizning Mentoringiz (yo'nalish beraman, real kod namunalari va tushuntirishlar bilan qo'llab-quvvatlayman, natijalarni tekshiraman).

---

## 📌 Status belgilari:
- `[ ]` — Bajarilmagan
- `[/]` — Jarayonda
- `[x]` — Bajarildi va tekshirildi

---

## 1-BOSQICH (1-kun): Muhitni sozlash, Loyiha arxitekturasi va Custom User modeli

### 🎯 Maqsad:
Kutubxonalarni o'rnatish, loyiha tuzilmasini yaratish va eng muhimi — birinchi `migrate` dan oldin to'g'ri **Custom User** modelini va uning Managerini yaratish.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 1.1. `requirements.txt`
Loyihaning ildiz papkasida `requirements.txt` faylini yarating va quyidagi kutubxonalarni yozing:

```txt
Django>=5.0,<6.0
djangorestframework>=3.15.0
djangorestframework-simplejwt>=5.3.0
psycopg[binary]>=3.1.0
python-dotenv>=1.0.0
django-environ>=0.11.0
django-filter>=24.0
django-cors-headers>=4.3.0
drf-spectacular>=0.27.0
aiogram>=3.4.0
httpx>=0.27.0
pytest>=8.0.0
pytest-django>=4.8.0
```
Terminalda o'rnatish:
```bash
pip install -r requirements.txt
```

---

#### 1.2. Loyiha strukturasi
Loyiha papkasida `config` loyihasini va `apps` papkasini tashkil qiling:
```bash
django-admin startproject config .
mkdir apps
# Windows PowerShell uchun bo'sh __init__.py yaratish:
New-Item -ItemType File apps/__init__.py
```

`users` app'ini yaratish:
```bash
python manage.py startapp users apps/users
```

---

#### 1.3. `.env` va `config/settings.py` sozlash
`.env` faylini quyidagicha to'ldiring:
```env
DEBUG=True
SECRET_KEY=django-insecure-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Asia/Tashkent

DB_NAME=evently
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_BOT_USERNAME=your_bot_username
BOT_API_SECRET=my-very-secure-secret-token-123
BACKEND_API_URL=http://localhost:8000/api/v1
REMINDER_HOURS_BEFORE=24
```

`config/settings.py` ichida:
```python
import os
from pathlib import Path
from datetime import timedelta
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # Local apps
    'apps.users',
    # 'apps.events',         # keyingi qadamlarda qo'shiladi
    # 'apps.notifications',  # keyingi qadamlarda qo'shiladi
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Eng tepada bo'lishi maqsadga muvofiq
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Database sozlamasi
DATABASES = {
    'default': env.db_url('DATABASE_URL', default=f"postgres://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}")
}

# Vaqt mintaqasi
TIME_ZONE = env('TIME_ZONE', default='Asia/Tashkent')
USE_TZ = True

# Custom User Model (Migratsiyadan oldin shart!)
AUTH_USER_MODEL = 'users.User'
```

---

#### 1.4. Custom User modeli va Manager (`apps/users/models.py`)
> ⚠️ **Muhim:** `AbstractUser` da login `username` orqali bo'ladi. Bizga esa **email** orqali kerak. Shuning uchun `UserManager` ni qayta yozishimiz shart.

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """Email orqali foydalanuvchi yaratuvchi Custom Manager"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser is_staff=True bo'lishi shart.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi shart.")

     
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    username = None  # username maydonini olib tashlaymiz
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    
    # Telegram integratsiyasi uchun
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_link_token = models.CharField(max_length=64, null=True, blank=True, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # createsuperuser da faqat email va password so'raladi

    def __str__(self):
        return f"{self.email} ({self.role})"
```

---

#### 1.5. Django Admin (`apps/users/admin.py`)
```python
# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'telegram_chat_id', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('id',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),
        ('Telegram', {'fields': ('telegram_chat_id', 'telegram_link_token')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'role', 'first_name', 'last_name'),
        }),
    )
```

---

#### 1.6. Migratsiya va Admin yaratish
```bash
python manage.py makemigrations users
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 2-BOSQICH (2-kun): Autentifikatsiya (JWT), Profil va Swagger

### 🎯 Maqsad:
Register, Login, Token Refresh, `GET/PATCH /auth/me/` endpointlarini va Swagger hujjatlarini ulash.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 2.1. SimpleJWT va DRF Sozlamalari (`config/settings.py`)
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(env('ACCESS_TOKEN_LIFETIME_MINUTES', default=60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(env('REFRESH_TOKEN_LIFETIME_DAYS', default=7))),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Evently API',
    'DESCRIPTION': 'Tadbirlarni boshqarish platformasi backend API hujjati',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

---

#### 2.2. Auth Serializer'lari (`apps/users/serializers.py`)
```python
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number', 'role')
        read_only_fields = ('id', 'role')  # XAVFSIZLIK: Foydalanuvchi o'zini admin qilib yuborolmaydi!

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Parollar bir xil emas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'telegram_chat_id', 'date_joined')
        read_only_fields = ('id', 'email', 'role', 'telegram_chat_id', 'date_joined')
```

---

#### 2.3. Auth View'lari (`apps/users/views.py`)
```python
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserMeSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
```

---

#### 2.4. URL'larni ulash (`apps/users/urls.py` va `config/urls.py`)
```python
# apps/users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserMeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user_me'),
]
```

`config/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    
    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## 3-BOSQICH (3-kun): Event modeli, Admin CRUD va Permission'lar

### 🎯 Maqsad:
`Event` modelini yaratish, Custom Permission'lar (`IsAdmin`, `IsAdminOrReadOnly`) va tadbir yaratish/tahrirlash/o'chirish logikasi.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 3.1. Permissions (`apps/users/permissions.py`)
```python
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Faqat role='admin' bo'lgan foydalanuvchilar uchun"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsAdminOrReadOnly(permissions.BasePermission):
    """GET/HEAD/OPTIONS hammaga, o'zgartirish faqat adminga"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
```

---

#### 3.2. `Event` modeli (`apps/events/models.py`)
```python
from django.db import models
from django.conf import settings

class Event(models.Model):
    class EventType(models.TextChoices):
        SEMINAR = 'seminar', 'Seminar'
        MASTERCLASS = 'masterclass', 'Masterclass'
        TRAINING = 'training', 'Training'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    location = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Null bo'lsa cheklanmagan")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_at']

    def __str__(self):
        return self.title
```

---

#### 3.3. Event Serializer (`apps/events/serializers.py`)
```python
from rest_framework import serializers
from django.utils import timezone
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'event_type', 'location',
            'start_at', 'end_at', 'capacity', 'status', 'created_by',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'created_by', 'created_at', 'updated_at')

    def validate(self, attrs):
        start_at = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end_at = attrs.get('end_at', getattr(self.instance, 'end_at', None))

        # BR-7: end_at har doim start_at dan keyin bo'lishi kerak
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."})

        # BR-8: Yangi yaratilayotganda o'tgan sanaga tadbir yaratib bo'lmaydi
        if not self.instance and start_at and start_at <= timezone.now():
            raise serializers.ValidationError({"start_at": "Tadbir boshlanish vaqti kelajakda bo'lishi kerak."})

        return attrs
```

---

#### 3.4. Event Views (`apps/events/views.py`)
```python
from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer
from apps.users.permissions import IsAdminOrReadOnly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

---

## 4-BOSQICH (4-kun): Qidiruv, Filtrlash, Pagination va Query Optimizatsiyasi (N+1 Muammosi)

> **Mentor eslatmasi:**  
> "Bazada 10 000 ta tadbir bo'lsa, ularni birdaniga olib kelish serverni o'ldiradi. Shuning uchun sahifalash (Pagination) kerak. Shuningdek, har bir tadbir bilan uning tashkilotchisini tortib olishda N+1 ta so'rov ketmasligi uchun `select_related` ishlatamiz."

### 🎯 Maqsad:
`registered_count`, `available_seats` maydonlarini optimal SQL so'rov orqali hisoblash, N+1 muammosini yo'qotish, qidiruv, tartiblash, sana oralig'i bo'yicha filtrlash va pagination tizimini to'liq joriy etish.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 4.1. Sahifalash (Pagination) sozlamasi (`apps/common/pagination.py` va `config/settings.py`)
- 📁 **Qaysi faylga:** `apps/common/pagination.py`
```python
# apps/common/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

- 📁 **Qaysi faylga:** `config/settings.py`
```python
# config/settings.py
REST_FRAMEWORK = {
    # ...
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
}
```
> 💡 **Izoh:** Har bir so'rovda server default 10 ta tadbir qaytaradi, foydalanuvchi `?page=2` yoki `?page_size=20` orqali boshqarishi mumkin.

---

#### 4.2. Filter klassini yaratish (`apps/events/filters.py`)
- 📁 **Qaysi faylga:** `apps/events/filters.py`
```python
# apps/events/filters.py
import django_filters
from django.utils import timezone
from .models import Event

class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateTimeFilter(field_name='start_at', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='start_at', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Event.Status.choices)
    event_type = django_filters.ChoiceFilter(choices=Event.EventType.choices)
    upcoming = django_filters.BooleanFilter(method='filter_upcoming')

    class Meta:
        model = Event
        fields = ['status', 'event_type', 'date_from', 'date_to', 'upcoming']

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(start_at__gt=timezone.now())
        return queryset
```
> 💡 **Izoh:** Foydalanuvchilar `/api/v1/events/?status=open&date_from=2026-12-01T00:00:00Z&event_type=seminar` ko'rinishida parametrlarga ko'ra tadbirlarni saralay oladi.

---

#### 4.3. Serializer'da bo'sh joylar va hisoblangan maydonlarni chiqarish (`apps/events/serializers.py`)
- 📁 **Qaysi faylga:** `apps/events/serializers.py`
```python
# apps/events/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.SerializerMethodField(read_only=True)
    organizer_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'location',
            'start_at', 'end_at', 'capacity', 'status',
            'registered_count', 'available_seats', 'organizer_email',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'status', 'created_by', 'created_at', 'updated_at',
            'registered_count', 'available_seats', 'organizer_email'
        ]

    def get_available_seats(self, obj):
        if obj.capacity is None:
            return None  # Cheklanmagan o'rinlar
        count = getattr(obj, 'registered_count', 0)
        return max(0, obj.capacity - count)

    def validate(self, attrs):
        start_at = attrs.get('start_at', getattr(self.instance, 'start_at', None))
        end_at = attrs.get('end_at', getattr(self.instance, 'end_at', None))

        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."})

        if not self.instance and start_at and start_at <= timezone.now():
            raise serializers.ValidationError({"start_at": "Tadbir boshlanish vaqti kelajakda bo'lishi kerak."})

        return attrs

    def validate_capacity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Capacity 0 dan katta bo'lish shart!")
        return value
```

---

#### 4.4. ViewSet: Query Optimizatsiyasi (N+1 ni yo'qotish), Filter, Qidiruv va Tartiblash (`apps/events/views.py`)
- 📁 **Qaysi faylga:** `apps/events/views.py`
```python
# apps/events/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Event
from .serializers import EventSerializer
from .filters import EventFilter
from .permissions import IsAdminOrReadonly

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadonly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_at', 'created_at', 'title']
    ordering = ['-start_at']

    def get_queryset(self):
        """
        N+1 muammosini yo'qotish uchun:
        - select_related('created_by'): muallif ma'lumotlarini bitta JOIN bilan tortadi
        - annotate(registered_count=...): tasdiqlangan ro'yxatdan o'tganlar sonini SQL COUNT orqali hisoblaydi
        """
        return Event.objects.select_related('created_by').annotate(
            registered_count=Count(
                'registrations',
                filter=Q(registrations__status='confirmed') | Q(registrations__status='active'),
                distinct=True
            )
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```
> 💡 **Izoh:**
> - `select_related('created_by')`: Tashkilotchi ma'lumotlari bitta SQL JOIN orqali olinadi (100 ta alohida SQL so'rov ketmaydi).
> - `annotate(...)`: Ro'yxatdan o'tganlar soni DB darajasida hisoblanadi.
> - `filters.SearchFilter`: `?search=python` orqali sarlavha, tavsif va manzildan qidiradi.
> - `filters.OrderingFilter`: `?ordering=start_at` yoki `?ordering=-created_at` orqali tartiblaydi.

---

#### 4.5. Tekshirish va Sinov (Verification)
1. Ro'yxatni pagination bilan olish:
   `GET /api/v1/events/?page=1&page_size=10`
2. Qidiruv va sana oralig'i:
   `GET /api/v1/events/?search=python&date_from=2026-11-20T00:00:00Z`
3. Status va tartiblash:
   `GET /api/v1/events/?status=open&ordering=start_at`
4. SQL so'rovlar sonini tekshirish: N+1 so'rovlar yo'qligini, tashkilotchi va ro'yxatdan o'tganlar soni bitta so'rovda hisoblanayotganini tekshirish.

---

## 5-BOSQICH (5-kun): Ro'yxatdan o'tish (Registration) Tizimi va Race Condition Muammosi

> **Mentor eslatmasi:**  
> "Tadbirda atigi 1 ta joy qolganda 10 kishi birdaniga ariza bersa, oddiy tekshiruv ish bermaydi va 1 ta joyga 10 kishi yozilib ketadi (Race Condition). Buni yechish uchun biz `transaction.atomic()` va PostgreSQL darajasida qatorni qulflash — `select_for_update()` dan foydalanamiz."

### 🎯 Maqsad:
Alohida `apps/registrations` ilovasini yaratish, `Registration` modelini tuzish, `select_for_update()` orqali Race Condition xavfini bartaraf etuvchi ro'yxatdan o'tish (Service Layer) biznes mantiqini va `POST /api/v1/events/{id}/register/` API endpointini joriy etish.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 5.1. Yangi ilova yaratish (`apps/registrations`) va sozlash
- 💻 **Terminalda bajarish:**
```bash
python manage.py startapp registrations apps/registrations
```

- 📁 **Qaysi faylga:** `apps/registrations/apps.py`
```python
# apps/registrations/apps.py
from django.apps import AppConfig

class RegistrationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.registrations'
```

- 📁 **Qaysi faylga:** `config/settings.py`
```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    # Local apps
    'apps.users',
    'apps.events',
    'apps.registrations',  # <-- yangi qo'shiladi
]
```
> 💡 **Izoh:** Ro'yxatdan o'tishlar va chiptalar tarixini modulli arxitektura asosida alohida toza ilovada yuritish uchun yangi ilova ochiladi va Django sozlamalariga ulanadi.

---

#### 5.2. `Registration` modeli va Unikal Constraint (`apps/registrations/models.py`)
- 📁 **Qaysi faylga:** `apps/registrations/models.py`
```python
# apps/registrations/models.py
from django.db import models
from django.conf import settings
from apps.events.models import Event

class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # BR-1: Bitta foydalanuvchi ayni bitta tadbirda faqat bitta aktiv ro'yxatga ega bo'lishi mumkin
            models.UniqueConstraint(
                fields=['user', 'event'],
                condition=models.Q(status='confirmed'),
                name='unique_active_user_event_registration'
            )
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.event.title} ({self.status})"
```
> 💡 **Izoh:** 
> - `related_name='registrations'` orqali 4-bosqichda yozilgan `Event.objects.annotate(registered_count=Count('registrations', ...))` to'g'ridan-to'g'ri ishlab ketadi.
> - `UniqueConstraint` esa ma'lumotlar bazasi darajasida bitta odam ayni bitta tadbirga bir vaqtda qayta-qayta yozilishining oldini oladi.

---

#### 5.3. Race Condition'ni yenguvchi Biznes Servis (`apps/registrations/services.py`)
- 📁 **Qaysi faylga:** `apps/registrations/services.py` [YANGI FAYL]
```python
# apps/registrations/services.py
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.events.models import Event
from .models import Registration

def register_user_to_event(user, event_id: int) -> Registration:
    """
    Foydalanuvchini tadbirga ro'yxatdan o'tkazish xizmati.
    Race Condition oldini olish uchun PostgreSQL darajasida 'select_for_update()' ishlatiladi.
    """
    with transaction.atomic():
        # 1. Tadbir qatorini qulflaymiz (Race condition ga qarshi)
        try:
            event = Event.objects.select_for_update().get(id=event_id)
        except Event.DoesNotExist:
            raise ValidationError({"detail": "Tadbir topilmadi.", "code": "event_not_found"})

        # 2. BR-5: Yopilgan yoki bekor qilingan tadbirga yozilib bo'lmaydi
        if event.status in [Event.Status.CLOSED, Event.Status.CANCELLED]:
            raise ValidationError({"detail": "Tadbir ro'yxatdan o'tish uchun yopiq.", "code": "event_closed"})

        # 3. BR-3: Boshlanib ketgan tadbirga yozilib bo'lmaydi
        if event.start_at <= timezone.now():
            raise ValidationError({"detail": "Tadbir allaqachon boshlangan yoki o'tib ketgan.", "code": "event_started"})

        # 4. BR-1: Foydalanuvchi allaqachon aktiv yozilgan bo'lsa rad etiladi
        existing_reg = Registration.objects.filter(user=user, event=event).first()
        if existing_reg and existing_reg.status == Registration.Status.CONFIRMED:
            raise ValidationError({"detail": "Siz bu tadbirga allaqachon ro'yxatdan o'tgansiz.", "code": "already_registered"})

        # 5. BR-2: Sig'im (capacity) tekshiruvi
        if event.capacity is not None:
            confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
            if confirmed_count >= event.capacity:
                # O'rinlar to'lgan bo'lsa statusni avtomatik FULL qilamiz
                if event.status != Event.Status.FULL:
                    event.status = Event.Status.FULL
                    event.save(update_fields=['status', 'updated_at'])
                raise ValidationError({"detail": "Ushbu tadbirda bo'sh joy qolmagan!", "code": "event_full"})

        # 6. Agar avval ro'yxatdan o'tib, keyin bekor qilgan bo'lsa — qayta CONFIRMED qilamiz
        if existing_reg and existing_reg.status == Registration.Status.CANCELLED:
            existing_reg.status = Registration.Status.CONFIRMED
            existing_reg.cancelled_at = None
            existing_reg.save(update_fields=['status', 'cancelled_at'])
            return existing_reg

        # 7. Yangi ro'yxatdan o'tishni yaratamiz
        return Registration.objects.create(
            user=user,
            event=event,
            status=Registration.Status.CONFIRMED
        )
```
> 💡 **Nega kerak (Izoh):**
> Bir soniyada 100 ta so'rov kelsa ham, `select_for_update()` PostgreSQL darajasida tadbir qatorini qulflaydi va so'rovlarni bittalab navbatga qo'yadi. Birinchi odam o'rinni egallab to'ldirishi bilan, navbatdagi so'rovlar "Bo'sh joy qolmagan" xatosini oladi.

---

#### 5.4. Serializer va View (`apps/registrations/serializers.py` va `apps/registrations/views.py`)
- 📁 **Qaysi faylga:** `apps/registrations/serializers.py` [YANGI FAYL]
```python
# apps/registrations/serializers.py
from rest_framework import serializers
from .models import Registration

class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id',
            'event',
            'event_title',
            'user',
            'user_email',
            'status',
            'created_at',
            'reminder_sent',
        ]
        read_only_fields = [
            'id',
            'event',
            'event_title',
            'user',
            'user_email',
            'status',
            'created_at',
            'reminder_sent',
        ]
```

- 📁 **Qaysi faylga:** `apps/registrations/views.py`
```python
# apps/registrations/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegistrationSerializer
from .services import register_user_to_event

class EventRegisterView(APIView):
    """
    POST /api/v1/events/{event_id}/register/
    Foydalanuvchini tadbirga ro'yxatdan o'tkazish endpointi
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id: int):
        registration = register_user_to_event(user=request.user, event_id=event_id)
        serializer = RegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

#### 5.5. URL marshrutlarini ulash (`apps/registrations/urls.py` va `config/urls.py`)
- 📁 **Qaysi faylga:** `apps/registrations/urls.py` [YANGI FAYL]
```python
# apps/registrations/urls.py
from django.urls import path
from .views import EventRegisterView

urlpatterns = [
    path('events/<int:event_id>/register/', EventRegisterView.as_view(), name='event-register'),
]
```

- 📁 **Qaysi faylga:** `config/urls.py`
```python
# config/urls.py
urlpatterns = [
    # ...
    path('api/v1/', include('apps.registrations.urls')),
]
```

---

#### 5.6. Migratsiyalarni yaratish va bazaga qo'llash
- 💻 **Terminalda bajarish:**
```bash
python manage.py makemigrations registrations
python manage.py migrate
```
> 💡 **Natija:** Bazada `registrations_registration` jadvali va unikal indeks hosil bo'ladi. Shu bilan birga, 4-bosqichdagi `apps/events/views.py` dagi `registered_count = Count('registrations', ...)` xatosi butunlay yo'qolib, avtomatik ishlab ketadi!

---

#### 5.7. Tekshirish va Sinov (Verification)
1. **Tadbirga yozilish:**
   - So'rov: `POST /api/v1/events/1/register/` (Header: `Authorization: Bearer <TOKEN>`)
   - Natija: `201 Created` va ro'yxatdan o'tish ma'lumotlari qaytadi.
2. **Qayta yozilishga urinish:**
   - Xuddi shu so'rov yana yuborilganda: `400 Bad Request` ("Siz bu tadbirga allaqachon ro'yxatdan o'tgansiz").
3. **4-bosqich API'sini tekshirish:**
   - So'rov: `GET /api/v1/events/`
   - Natija: Endi xato bermaydi! `registered_count: 1` va `available_seats: 99` deb bazadan to'g'ri hisoblab qaytaradi.

---

## 6-BOSQICH (6-kun): Tadbirdan chiqish, Mening tadbirlarim va Admin yopish

### 🎯 Maqsad:
Ro'yxatdan chiqish (BR-6), o'z yozilishlarini ko'rish (BR-10), admin tadbirni yopishi va qatnashuvchilar ro'yxati.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 6.1. Chiqish servisi (`apps/events/services.py`)
```python
def unregister_user_from_event(user, event_id):
    with transaction.atomic():
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise ValidationError({"detail": "Tadbir topilmadi.", "code": "not_found"})

        # BR-6: Tadbir boshlangandan keyin chiqib bo'lmaydi
        if event.start_at <= timezone.now():
            raise ValidationError({"detail": "Tadbir boshlangan, undan chiqib bo'lmaydi.", "code": "event_started"})

        reg = Registration.objects.filter(user=user, event=event, status=Registration.Status.ACTIVE).first()
        if not reg:
            raise ValidationError({"detail": "Siz bu tadbirga yozilmagansiz.", "code": "not_registered"})

        reg.status = Registration.Status.CANCELLED
        reg.cancelled_at = timezone.now()
        reg.save()
        return reg
```

---

#### 6.2. Action Endpointlari (`apps/events/views.py`)
```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions
from .services import register_user_to_event, unregister_user_from_event
from apps.users.permissions import IsAdmin

class EventViewSet(viewsets.ModelViewSet):
    # ... avvalgi kodlar ...

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, pk=None):
        reg = register_user_to_event(request.user, pk)
        return Response({"id": reg.id, "status": reg.status, "created_at": reg.created_at}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unregister(self, request, pk=None):
        reg = unregister_user_from_event(request.user, pk)
        return Response({"detail": "Tadbirdan muvaffaqiyatli chiqdingiz.", "status": reg.status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def close(self, request, pk=None):
        event = self.get_object()
        event.status = Event.Status.CLOSED
        event.save()
        return Response({"detail": "Tadbir muvaffaqiyatli yopildi.", "status": event.status})

    @action(detail=True, methods=['get'], permission_classes=[IsAdmin])
    def participants(self, request, pk=None):
        event = self.get_object()
        active_regs = event.registrations.filter(status=Registration.Status.ACTIVE).select_related('user')
        data = [{
            "registration_id": r.id,
            "user_id": r.user.id,
            "full_name": f"{r.user.first_name} {r.user.last_name}".strip(),
            "email": r.user.email,
            "phone_number": r.user.phone_number,
            "registered_at": r.created_at
        } for r in active_regs]
        return Response({"count": len(data), "results": data})
```

---

## 7-BOSQICH (7-kun): Telegram Bot Integratsiyasi va Xabarnomalar (`apps/notifications` va `bot/`)

> **Mentor eslatmasi:**  
> "Telegram bot — bu Django ichida emas, alohida mustaqil jarayon sifatida ishlovchi asinxron mikroxizmat. U bazaga to'g'ridan-to'g'ri kirmaydi, balki biz yaratgan REST API bilan alohida `api_client.py` orqali aloqa qiladi. Backend tomonida esa barcha Telegram logikasi (token generatsiya qilish, tasdiqlash, xabar yuborish) modulli arxitektura asosida toza **`apps/notifications`** ilovasida jamlanadi."

### 🎯 Maqsad:
Loyiha arxitekturasini toza va professional ko'rinishga keltirish:
1. **`apps/notifications`**: Telegram bilan ishlash bo'yicha Backend servislar (`services.py`), xavfsiz endpointlar (`views.py`: `/telegram/link/`, `/telegram/confirm/`, `/telegram/my-events/`), URL yo'riqnomasi (`urls.py`) va testlar (`tests/`).
2. **`bot/`**: Aiogram 3 da ishlovchi mustaqil bot: sozlamalar (`config.py`), Backend API bilan aloqa mijozi (`api_client.py`), buyruqlar va xabar handlerlari (`handlers.py`) hamda bot ishga tushirish fayli (`main.py`).

---

### 📁 Ko'zda tutilgan Katalog Strukturasi:
```
apps/
└── notifications/             # Telegram va xabarnomalar moduli
    ├── __init__.py
    ├── apps.py
    ├── services.py            # send_message, notify_registration_success
    ├── views.py               # /telegram/link/, /telegram/confirm/, /telegram/my-events/
    ├── urls.py
    └── tests/
        ├── __init__.py
        └── test_telegram_api.py

bot/                           # Aiogram 3 bot (alohida jarayon)
├── __init__.py
├── config.py                  # Bot sozlamalari (.env dan o'qish)
├── api_client.py              # Backend API bilan ishlash (httpx)
├── handlers.py                # /start, /start <token>, /my_events handlerlari
└── main.py                    # Bot polling va Dispatcher ishga tushirish
```

---

### 📋 Vazifalar va Real Kod Misollari:

#### 7.1. Yangi ilova yaratish (`apps/notifications`) va sozlash
- 💻 **Terminalda bajarish:**
```bash
python manage.py startapp notifications apps/notifications
```

- 📁 **Qaysi faylga:** `apps/notifications/apps.py`
```python
# apps/notifications/apps.py
from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications and Telegram'
```

- 📁 **Qaysi faylga:** `config/settings.py`
```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    # Local apps
    'apps.users',
    'apps.events',
    'apps.registrations',
    'apps.notifications',  # <-- yangi qo'shiladi
]
```
> 💡 **Nega kerak (Izoh):** Telegram va bildirishnomalar bilan bog'liq xizmatlarni boshqa ilovalarga qorishtirmasdan, mustaqil `apps/notifications` app ichida ajratish.

---

#### 7.2. Telegram Xabarnoma Servislari (`apps/notifications/services.py`)
- 📁 **Qaysi faylga:** `apps/notifications/services.py` [YANGI FAYL]
```python
# apps/notifications/services.py
import logging
import httpx
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id: int, text: str) -> bool:
    """
    Telegram Bot API orqali ko'rsatilgan chat_id ga xabar yuborish.
    HTML teglarni qo'llab-quvvatlaydi.
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan, xabar yuborilmadi.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = httpx.post(url, json=payload, timeout=5.0)
        if response.is_success:
            return True
        logger.error(f"Telegram API xatosi ({response.status_code}): {response.text}")
        return False
    except Exception as e:
        logger.error(f"Telegram xabari yuborishda ulanish nosozligi: {e}")
        return False

def notify_registration_success(registration) -> None:
    """
    Foydalanuvchi tadbirga muvaffaqiyatli yozilganda Telegram xabari yuborish.
    Tranzaksiya muvaffaqiyatli commit bo'lgandan keyin ishlaydi (on_commit).
    """
    def _send():
        user = registration.user
        event = registration.event
        if user.telegram_chat_id:
            msg = (
                f"🎉 <b>Tabriklaymiz, siz tadbirga muvaffaqiyatli yozildingiz!</b>\n\n"
                f"📌 <b>{event.title}</b>\n"
                f"🗓 <b>Vaqti:</b> {event.start_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📍 <b>Manzil:</b> {event.location}\n"
                f"🔖 <b>Chipta ID:</b> #{registration.id}\n\n"
                f"Tadbir haqida eslatma 24 soat oldin ushbu bot orqali yuboriladi!"
            )
            send_telegram_message(user.telegram_chat_id, msg)

    transaction.on_commit(_send)
```
> 💡 **Nega kerak (Izoh):** Ushbu servis orqali ham ro'yxatdan o'tishdagi xabarlar, ham 8-bosqichdagi 24 soatlik eslatmalar Telegram orqali bitta markazlashgan funksiya vositasida yuboriladi.

---

#### 7.3. Bog'lash va API Ko'rinishlari (`apps/notifications/views.py`)
- 📁 **Qaysi faylga:** `apps/notifications/views.py`
```python
# apps/notifications/views.py
import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from apps.registrations.models import Registration

User = get_user_model()

class TelegramLinkGenerateView(APIView):
"""
    POST /api/v1/notifications/telegram/link/
    Tizimga kirgan foydalanuvchiga 32 baytlik xavfsiz bir martalik token
    generatsiya qiladi va Telegram bot Deep-link havolasini taqdim etadi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = secrets.token_urlsafe(32)
        user.telegram_link_token = token
        user.save(update_fields=['telegram_link_token'])

        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'myeventlyBot')
        bot_url = f"https://t.me/{bot_username}?start={token}"

        return Response({
            "token": token,
            "bot_url": bot_url,
            "message": "Ushbu havola orqali botga o'ting va 'Start' tugmasini bosing."
        }, status=status.HTTP_200_OK)


class TelegramConfirmView(APIView):
    """
    POST /api/v1/notifications/telegram/confirm/
    Aiogram bot tomonidan tokenni tasdiqlash uchun chaqiriladi.
    Xavfsizlik: X-Bot-Secret header tekshiriladi.
    Body: {"token": "...", "chat_id": 123456789}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        bot_secret = request.headers.get('X-Bot-Secret')
        expected_secret = getattr(settings, 'BOT_API_SECRET', None)

        if not expected_secret or bot_secret != expected_secret:
            return Response(
                {"detail": "Ruxsat berilmagan so'rov (X-Bot-Secret noto'g'ri)."},
                status=status.HTTP_403_FORBIDDEN
            )

        token = request.data.get('token')
        chat_id = request.data.get('chat_id')

        if not token or not chat_id:
            return Response(
                {"detail": "token va chat_id talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(telegram_link_token=token)
        except User.DoesNotExist:
            return Response(
                {"detail": "Havola eskirgan yoki token yaroqsiz."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Agar bu chat_id boshqa userga tegishli bo'lgan bo'lsa, avvalgisini bo'shatamiz
        User.objects.filter(telegram_chat_id=chat_id).exclude(id=user.id).update(telegram_chat_id=None)

        # Chat ID ni biriktiramiz va tokenni yoqib yuboramiz (bir martalik)
        user.telegram_chat_id = chat_id
        user.telegram_link_token = None
        user.save(update_fields=['telegram_chat_id', 'telegram_link_token'])

        return Response({
            "detail": "Hisobingiz muvaffaqiyatli bog'landi.",
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip()
        }, status=status.HTTP_200_OK)


class TelegramUserEventsView(APIView):
    """
    POST /api/v1/notifications/telegram/my-events/
    Aiogram bot foydalanuvchining chat_id si bo'yicha uning aktiv tadbirlarini so'raydi.
    Header: X-Bot-Secret
    Body: {"chat_id": 123456789}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        bot_secret = request.headers.get('X-Bot-Secret')
        expected_secret = getattr(settings, 'BOT_API_SECRET', None)

        if not expected_secret or bot_secret != expected_secret:
            return Response({"detail": "Taqiqlangan so'rov."}, status=status.HTTP_403_FORBIDDEN)

        chat_id = request.data.get('chat_id')
        if not chat_id:
            return Response({"detail": "chat_id talab qilinadi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(telegram_chat_id=chat_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Ushbu Telegram akkauntga bog'langan foydalanuvchi topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        registrations = (
            Registration.objects
            .filter(user=user, status=Registration.Status.CONFIRMED)
            .select_related('event')
            .order_by('event__start_at')
        )

        events_data = [
            {
                "registration_id": reg.id,
                "event_title": reg.event.title,
                "event_type": reg.event.event_type,
                "location": reg.event.location,
                "start_at": reg.event.start_at.strftime('%Y-%m-%d %H:%M'),
                "status": reg.event.status,
            }
            for reg in registrations
        ]

        return Response({
            "user_email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "count": len(events_data),
            "events": events_data
        }, status=status.HTTP_200_OK)
```
> 💡 **Nega kerak (Izoh):** Sayt foydalanuvchisi uchun havola yaratish, bot uchun esa maxfiy kalit bilan himoyalangan token tasdiqlash (`/confirm/`) va shaxsiy tadbirlarni olish (`/my-events/`) API interfeyslarini ta'minlaydi.

---

#### 7.4. Notifications URL marshrutlari (`apps/notifications/urls.py` va `config/urls.py`)
- 📁 **Qaysi faylga:** `apps/notifications/urls.py` [YANGI FAYL]
```python
# apps/notifications/urls.py
from django.urls import path
from .views import (
    TelegramLinkGenerateView,
    TelegramConfirmView,
    TelegramUserEventsView,
)

urlpatterns = [
    path('telegram/link/', TelegramLinkGenerateView.as_view(), name='telegram_link'),
    path('telegram/confirm/', TelegramConfirmView.as_view(), name='telegram_confirm'),
    path('telegram/my-events/', TelegramUserEventsView.as_view(), name='telegram_my_events'),
]
```

- 📁 **Qaysi faylga:** `config/urls.py`
```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/', include('apps.events.urls')),
    path('api/v1/', include('apps.registrations.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),  # <-- yangi ulanadi
    # ... Swagger sxemalari
]
```
> 💡 **Nega kerak (Izoh):** Barcha Telegram endpointlari `/api/v1/notifications/telegram/...` ostida tartibli jamlanadi.

---

#### 7.5. Unit Testlar (`apps/notifications/tests/test_telegram_api.py`)
- 📁 **Qaysi faylga:** `apps/notifications/tests/test_telegram_api.py` [YANGI FAYL]
```python
# apps/notifications/tests/test_telegram_api.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class TelegramAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            first_name="Ali",
            last_name="Valiyev"
        )
        self.bot_secret = getattr(settings, 'BOT_API_SECRET', 'my-very-secure-secret-token-123')

    def test_link_generate_requires_auth(self):
        # Autentifikatsiyasiz kirish taqiqlangan bo'lishi shart
        response = self.client.post('/api/v1/notifications/telegram/link/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_link_generate_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/v1/notifications/telegram/link/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('bot_url', response.data)

        # Bazada token saqlanganligini tekshiramiz
        self.user.refresh_from_db()
        self.assertEqual(self.user.telegram_link_token, response.data['token'])

    def test_confirm_without_secret_fails(self):
        response = self.client.post('/api/v1/notifications/telegram/confirm/', {
            "token": "dummy_token",
            "chat_id": 12345678
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_confirm_success(self):
        # 1. Token yaratamiz
        self.user.telegram_link_token = "valid_test_token_123"
        self.user.save()

        # 2. Bot nomidan to'g'ri header bilan tasdiqlaymiz
        response = self.client.post(
            '/api/v1/notifications/telegram/confirm/',
            data={"token": "valid_test_token_123", "chat_id": 99887766},
            format='json',
            HTTP_X_BOT_SECRET=self.bot_secret
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Bazadagi holatni tekshiramiz: chat_id birikkan, token esa None bo'lishi shart
        self.user.refresh_from_db()
        self.assertEqual(self.user.telegram_chat_id, 99887766)
        self.assertIsNone(self.user.telegram_link_token)
```
> 💡 **Nega kerak (Izoh):** Xavfsizlik, tokenning to'g'ri birikishi va begona so'rovlar bloklanishi kafolatini avtomatik test orqali tekshirish.

---

#### 7.6. Aiogram 3: Bot Konfiguratsiyasi (`bot/config.py`)
- 📁 **Qaysi faylga:** `bot/config.py` [YANGI FAYL]
```python
# bot/config.py
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env_file = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
BOT_API_SECRET = env('BOT_API_SECRET', default='my-very-secure-secret-token-123')
BACKEND_API_URL = env('BACKEND_API_URL', default='http://localhost:8000/api/v1')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN topilmadi! Iltimos, .env faylini to'ldiring.")
```
> 💡 **Nega kerak (Izoh):** Bot mustaqil jarayon bo'lib ishlaganda barcha parollar va backend manzilini `.env` orqali xavfsiz yuklaydi.

---

#### 7.7. Aiogram 3: Backend API Mijozi (`bot/api_client.py`)
- 📁 **Qaysi faylga:** `bot/api_client.py` [YANGI FAYL]
```python
# bot/api_client.py
import httpx
import logging
from bot.config import BACKEND_API_URL, BOT_API_SECRET

logger = logging.getLogger(__name__)

class BackendAPIClient:
    """
    Django Backend API bilan asinxron HTTP so'rovlar orqali
    aloqa o'rnatuvchi xizmatlar to'plami.
    """
    def __init__(self, base_url: str = BACKEND_API_URL, secret: str = BOT_API_SECRET):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-Bot-Secret": secret,
            "Content-Type": "application/json"
        }

    async def confirm_telegram_account(self, token: str, chat_id: int):
        """
        Deep-link token va chat_id ni backendga yuborib hisobni tasdiqlaydi.
        """
        url = f"{self.base_url}/notifications/telegram/confirm/"
        payload = {"token": token, "chat_id": chat_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
            return response
        except Exception as e:
            logger.error(f"confirm_telegram_account ulanish xatosi: {e}")
            return None

    async def get_user_events(self, chat_id: int):
        """
        Foydalanuvchining chat_id si bo'yicha tadbirlari ro'yxatini oladi.
        """
        url = f"{self.base_url}/notifications/telegram/my-events/"
        payload = {"chat_id": chat_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
            return response
        except Exception as e:
            logger.error(f"get_user_events ulanish xatosi: {e}")
            return None

# Singleton obyekt
api_client = BackendAPIClient()
```
> 💡 **Nega kerak (Izoh):** API bilan bog'liq barcha `httpx` so'rovlarini alohida `api_client.py` da jamlash handlerlarni qisqa, toza va oson o'qiladigan qiladi.

---

#### 7.8. Aiogram 3: Telegram Handlerlari (`bot/handlers.py`)
- 📁 **Qaysi faylga:** `bot/handlers.py` [YANGI FAYL]
```python
# bot/handlers.py
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject, Command
from bot.api_client import api_client

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    """
    /start yoki /start <token> komandasi.
    Foydalanuvchi akkauntini deep-link token orqali Evently profiliga bog'laydi.
    """
    token = command.args

    if not token:
        await message.answer(
            f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
            "👋 <b>Evently Telegram Boti</b>ga xush kelibsiz!\n\n"
            "Profilingizni sayt bilan bog'lash uchun, veb-saytimizdagi shaxsiy profilingizga kiring "
            "va <b>'Telegram bilan bog'lash'</b> tugmasini bosing.\n\n"
            "Agar akkauntingiz allaqachon ulangan bo'lsa, tadbirlaringizni ko'rish uchun /my_events buyrug'ini yuboring."
        )
        return

    # Deep-link token mavjud bo'lsa — Backend API orqali tasdiqlaymiz
    response = await api_client.confirm_telegram_account(token=token, chat_id=message.chat.id)

    if response is None:
        await message.answer("⚠️ Server bilan bog'lanishda nosozlik yuz berdi. Backend ishlayotganligini tekshiring.")
        return

    if response.status_code == 200:
        data = response.json()
        email = data.get('email', '')
        full_name = data.get('full_name', '')
        await message.answer(
            "🎉 <b>Tabriklaymiz!</b>\n\n"
            f"Hurmatli <b>{full_name or email}</b>, profilingiz Evently tizimiga muvaffaqiyatli bog'landi!\n\n"
            "Endi siz:\n"
            "• Tadbirlarga ro'yxatdan o'tganingizda darhol tasdiq xabarnomasini olasiz\n"
            "• Tadbir boshlanishiga 24 soat qolganda eslatmalar qabul qilasiz\n"
            "• /my_events buyrug'i orqali istalgan vaqtda barcha chiptalaringizni ko'ra olasiz."
        )
    elif response.status_code == 404:
        await message.answer(
            "❌ <b>Havola eskirgan yoki yaroqsiz!</b>\n\n"
            "Ushbu havoladan avval foydalanilgan yoki muddati tugagan. Iltimos, saytdan yangi havola oling."
        )
    else:
        await message.answer("⚠️ Akkauntni bog'lashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")


@router.message(Command("my_events"))
async def cmd_my_events(message: types.Message):
    """
    /my_events komandasi:
    Foydalanuvchining aktiv ro'yxatdan o'tgan tadbirlari ro'yxatini chiqaradi.
    """
    response = await api_client.get_user_events(chat_id=message.chat.id)

    if response is None:
        await message.answer("⚠️ Ma'lumotlarni olishda server bilan ulanish nosozligi.")
        return

    if response.status_code == 404:
        await message.answer(
            "❌ <b>Akkaunt bog'lanmagan!</b>\n\n"
            "Sizning Telegram hisobingiz tizimdagi hech qaysi profilga ulanmagan.\n"
            "Iltimos, saytdan profilingizga kiring va 'Telegram bilan bog'lash' tugmasini bosing."
        )
        return

    if response.status_code != 200:
        await message.answer("⚠️ Tadbirlarni yuklashda xatolik yuz berdi.")
        return

    data = response.json()
    events = data.get("events", [])

    if not events:
        await message.answer(
            f"👤 Hurmatli <b>{data.get('full_name') or data.get('user_email')}</b>,\n\n"
            "Hozirda siz ro'yxatdan o'tgan faol tadbirlar mavjud emas."
        )
        return

    text = f"📋 <b>Sizning tadbirlaringiz ({len(events)} ta):</b>\n\n"
    for idx, ev in enumerate(events, 1):
        text += (
            f"<b>{idx}. {ev['event_title']}</b>\n"
            f"🔹 Turi: {ev['event_type'].capitalize()}\n"
            f"🗓 Sana: {ev['start_at']}\n"
            f"📍 Manzil: {ev['location']}\n"
            f"🔖 Chipta holati: <i>{ev['status']}</i>\n"
            "─────────────────\n"
        )

    await message.answer(text)
```
> 💡 **Nega kerak (Izoh):** Botga kelgan har qanday `/start` va `/my_events` buyruqlari qisqa, aniq va xatoliklarni to'g'ri ushlaydigan ko'rinishda ishlaydi.

---

#### 7.9. Aiogram 3: Bot Asosiy Kirish Nuqtasi (`bot/main.py`)
- 📁 **Qaysi faylga:** `bot/main.py` [YANGI FAYL]
```python
# bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config import BOT_TOKEN
from bot.handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Evently Telegram Bot ishga tushmoqda...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Handlers routerni ulaymiz
    dp.include_router(router)

    # Eski kutilayotgan xabarlarni tozalab, pollingni boshlaymiz
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
```
> 💡 **Nega kerak (Izoh):** Aiogram 3 da asinxron polling rejimida botni ishga tushiruvchi markaziy kirish nuqtasi (`entry point`).

---

#### 7.10. Tekshirish va Sinov (Verification)
1. **API Testlarini ishga tushirish:**
   ```bash
   python manage.py test apps.notifications
   ```
2. **Bog'lash havolasini olish:**
   - So'rov: `POST /api/v1/notifications/telegram/link/`
   - Header: `Authorization: Bearer <USER_ACCESS_TOKEN>`
   - Natija: `200 OK` va `bot_url` olinadi.
3. **Botni ishga tushirish:**
   ```bash
   python -m bot.main
   ```
4. **Telegramda botni sinash:**
   - `bot_url` orqali kirib `/start` bosiladi -> Akkaunt bog'lanadi va tabrik xabari keladi.
   - Botda `/my_events` buyrug'i beriladi -> Foydalanuvchi tadbirlari ro'yxati ko'rsatiladi.

---

## 8-BOSQICH (8-kun): Eslatmalar mexanizmi (Management Command)

### 🎯 Maqsad:
`python manage.py send_event_reminders` komandasi orqali boshlanishiga 24 soat qolgan tadbirlar qatnashuvchilariga eslatma jo'natish.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 8.1. `send_event_reminders.py` (`apps/events/management/commands/send_event_reminders.py`)
```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Registration, Event
from apps.notifications.services import send_telegram_message

class Command(BaseCommand):
    help = "Tadbirga 24 soat qolganda qatnashuvchilarga eslatma yuborish"

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_limit = now + timedelta(hours=24)

        regs = Registration.objects.filter(
            status=Registration.Status.ACTIVE,
            reminder_sent=False,
            event__status=Event.Status.OPEN,
            event__start_at__gt=now,
            event__start_at__lte=reminder_limit,
            user__telegram_chat_id__isnull=False
        ).select_related('user', 'event')

        count = 0
        for reg in regs:
            text = (
                f"⏰ <b>Eslatma!</b>\n\n"
                f"Siz yozilgan tadbir yaqinlashmoqda:\n"
                f"📌 <b>{reg.event.title}</b>\n"
                f"🗓 {reg.event.start_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"📍 {reg.event.location}\n\n"
                f"Kechikmang!"
            )
            success = send_telegram_message(reg.user.telegram_chat_id, text)
            if success:
                reg.reminder_sent = True
                reg.save(update_fields=['reminder_sent'])
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ta eslatma muvaffaqiyatli yuborildi."))
```

---

## 9-BOSQICH (9-kun): Avtomatik Testlar (Testing)

### 🎯 Maqsad:
Biznes qoidalar va xavfsizlik talablarini Django `TestCase` orqali tekshirish.

---

### 📋 Vazifalar va Real Kod Misollari:

#### 9.1. Tadbirga yozilish testi (`apps/events/tests/test_registration.py`)
```python
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.events.models import Event, Registration
from apps.events.services import register_user_to_event
from rest_framework.exceptions import ValidationError

class RegistrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@user.com", password="password123")
        self.event = Event.objects.create(
            title="Python Masterclass",
            description="Dars",
            event_type="masterclass",
            location="Toshkent",
            start_at=timezone.now() + timedelta(days=2),
            end_at=timezone.now() + timedelta(days=2, hours=2),
            capacity=1
        )

    def test_successful_registration(self):
        reg = register_user_to_event(self.user, self.event.id)
        self.assertEqual(reg.status, Registration.Status.ACTIVE)

    def test_duplicate_registration_fails(self):
        register_user_to_event(self.user, self.event.id)
        # BR-1: Takroriy yozilish xato berishi shart
        with self.assertRaises(ValidationError):
            register_user_to_event(self.user, self.event.id)

    def test_capacity_full_fails(self):
        register_user_to_event(self.user, self.event.id)
        user2 = User.objects.create_user(email="user2@test.com", password="password123")
        # BR-2: Joy qolmaganda xato berishi shart
        with self.assertRaises(ValidationError):
            register_user_to_event(user2, self.event.id)
```

---

## 10-BOSQICH (10-kun): Deployment va Yakuniy Himoya

### 🎯 Maqsad:
Loyihani Render/Railway'ga chiqarish va himoyaga tayyorgarlik.

### 📋 Ko'rsatmalar:
1. `Procfile` yaratish:
   ```
   web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
   bot: python -m bot.main
   ```
2. `runtime.txt` yaratish (`python-3.11.8`).
3. Muhit o'zgaruvchilarini (`.env`) server dashboardiga kiritish (`DEBUG=False`).
4. Demo ssenariysini bir necha bor mustaqil Swagger orqali mashq qilish.

---

## 🚀 Qanday harakat qilamiz?
Endi sizda har bir qadam uchun **to'liq kod namunalari va tushuntirishlar** mavjud!  
Keling, hoziroq **1-BOSQICH (1-kun)** bo'yicha:
1. `requirements.txt` ni yaratish;
2. Kutubxonalarni o'rnatish;
3. `config` loyihasi va `apps/users` app'ini sozlashni boshlaylik.

Siz qaysi amaldan boshlayapsiz? Biror joyida yordam kerak bo'lsa darhol ayting!
