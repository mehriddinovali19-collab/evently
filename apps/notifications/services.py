import logging
import httpx
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id: int, text: str) -> bool:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
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
        logger.error(f"Telegram xabari yuborishda ulanish nosozligi:{e}")
        return False


def notify_registration_success(registration) -> None:

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