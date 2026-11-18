from django.contrib import admin                                                                                                                              
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
  
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
  

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Yangi yaratilgan formalarni bog'laymiz
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
  
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'telegram_chat_id', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('id',)
  
        # Mavjud foydalanuvchini tahrirlash sahifasi
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),
        ('Telegram', {'fields': ('telegram_chat_id', 'telegram_link_token')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )
  
    # Yangi foydalanuvchi qo'shish sahifasi (/admin/users/user/add/)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'first_name', 'last_name'), 
        }), 
    )