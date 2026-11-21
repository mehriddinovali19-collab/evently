from rest_framework import serializers
from .models import Registration
from apps.events.serializers import EventSerializer

class RegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Registration
        fields = (
            'id',
            'event',
            'event_title',
            'user',
            'user_email',
            'status',
            'created_at',
            'reminder_sent',
        )
        read_only_fields= (
            'id',
            'event',
            'event_title',
            'user',
            'user_email',
            'status',
            'created_at',
            'reminder_sent',
        )

class MyRegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = (
            'id',
            'event',
            'status',
            'created_at',
            'cancelled_at',
            'reminder_sent'
        )