from django.db import models
from django.conf import settings


class Event(models.Model):
    class EventType(models.TextChoices):
        SEMINAR = 'seminar', 'Seminar'
        MASTERCLASS = 'masterclass', 'Masterclass'
        TRAINING = 'training', 'Training'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        FULL = 'full', 'Full'
        CLOSED = 'closed', 'Closed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    location = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Null bo'lsa cheklanmangan")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="events")

    class Meta:
        ordering = ["-start_at"]



    def __str__(self):
        return self.title