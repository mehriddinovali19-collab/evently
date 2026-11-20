from django.contrib import admin
from .models import Event
  

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'status', 'start_at', 'capacity', 'created_by')
    list_filter = ('status', 'event_type', 'start_at')
    search_fields = ('title', 'location')
    date_hierarchy = 'start_at'