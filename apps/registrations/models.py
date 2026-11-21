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
        ordering = ["-created_at"]
        """ # BR-1: Bitta foydalanuvchi
            ayni bitta tadbirda faqat bitta 
            aktiv ro'yxatga ega bo'lishi mumkin"""

        constraints = [
              models.UniqueConstraint(
                  fields=['user', 'event'],
                   condition=models.Q(status='confirmed'),
                  name='unique_active_user_event_registration')
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.event.title} ({self.status})"
    
    


