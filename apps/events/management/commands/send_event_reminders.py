from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event
from apps.registrations.models import Registration
from apps.notifications.services import send_telegram_message

class Command(BaseCommand):
    help = "Tadbirga 24 soat qolganda qatnashuvchilarga eslatma yuborish"

    def handle(self, *args, **options):
        now = timezone.now()
        reminder_limit = now + timedelta(hours=24)

        regs = Registration.objects.filter(
            status= Registration.Status.CONFIRMED,
            reminder_sent= False,
            event__status= Event.Status.OPEN,
            event__start_at__gt= now,
            event__start_at__lte= reminder_limit,
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
                reg.reminder_sent= True
                reg.save(update_fields=['reminder_sent'])
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ta eslatma muvaffaqiyatli yuborildi."))