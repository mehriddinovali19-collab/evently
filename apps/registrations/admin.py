from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'status', 'created_at', 'reminder_sent')
    list_filter = ('status', 'reminder_sent', 'created_at')
    search_fields =  ('user__email', 'event__title')