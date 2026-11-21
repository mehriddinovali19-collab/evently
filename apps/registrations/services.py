from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.events.models import Event
from .models import Registration

def register_user_to_event(user, event_id: int ) -> Registration:
     """
    Foydalanuvchini tadbirga ro'yxatdan o'tkazish xizmati.
    Race Condition oldini olish uchun PostgreSQL darajasida 'select_for_update()' ishlatiladi.
    """
     with transaction.atomic():
          try:
               event = Event.objects.select_for_update().get(id=event_id)
          except Event.DoesNotExist:
               raise ValidationError({'detail':'Event Not Found.', 'code': 'event_not_found'})

          if event.status in [Event.Status.CLOSED, Event.Status.CANCELLED]:
               raise ValidationError({"detail": "Event had already closed to rigerter.", "code": 'event_closed'})

          if event.start_at <= timezone.now():
               raise ValidationError({'detail': 'This event had already started!', 'code': 'event_already_started'})

          existing_reg = Registration.objects.filter(user=user, event=event).first()
          if existing_reg and existing_reg.status == Registration.Status.CONFIRMED:
               raise ValidationError({'detail': 'User had already rigistered to the event!', "code": 'already_registered'})

          if event.capacity is not None:
            confirmed_count = event.registrations.filter(status=Registration.Status.CONFIRMED).count()
            if confirmed_count >= event.capacity:
                # O'rinlar to'lgan bo'lsa statusni avtomatik FULL qilamiz
                if event.status != Event.Status.FULL:
                    event.status = Event.Status.FULL
                    event.save(update_fields=['status', 'updated_at'])
                raise ValidationError({"detail": "Ushbu tadbirda bo'sh joy qolmagan!", "code": "event_full"})
            
          if existing_reg and existing_reg.status == Registration.Status.CANCELLED:                                                                                 
            existing_reg.status = Registration.Status.CONFIRMED                                                                                                   
            existing_reg.cancelled_at = None                                                                                                                      
            existing_reg.save(update_fields=['status', 'cancelled_at'])                                                                                           
            return existing_reg 

          return Registration.objects.create(user=user, event=event,status=Registration.Status.CONFIRMED)



def unregister_user_to_event(user, event_id: int) -> Registration:
    with transaction.atomic():
        try:
               event = Event.objects.select_for_update().get(id=event_id)
        except Event.DoesNotExist:
               raise ValidationError({'detail':'Event Not Found.', 'code': 'event_not_found'})

        if event.start_at <= timezone.now():
             raise ValidationError({'detail': 'Tadbir boshlangan, undan chiqib bo\'lmaydi.', 'code': 'event_already_started'})

        reg = Registration.objects.filter(user=user, event=event, status=Registration.Status.CONFIRMED).first()

        if not reg:
             raise ValidationError({'detail': 'Siz bu tadbirga ro\'yxatdan o\'tmagansiz.', 'code': 'not_registered'})
        reg.status = Registration.Status.CANCELLED
        reg.cancelled_at = timezone.now()
        reg.save(update_fields=['status', 'cancelled_at'])

        if event.status == Event.Status.FULL:
             event.status = Event.Status.OPEN
             event.save(update_fields=['status', 'updated_at'])

        return reg