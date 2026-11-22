import secrets
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from apps.registrations.models import Registration

User = get_user_model()

class TelegramLinkGenerateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        token = secrets.token_urlsafe(32)
        request.user.telegram_link_token = token
        user.save(update_fields=['telegram_link_token'])

        bot_username = getattr(settings, 'TELEGRAM_BOT_USERNAME', 'myeventlyBot')
        bot_url = f"https://t.me/{bot_username}?start={token}"

        return Response({
            "token": token,
            "bot_url": bot_url,
            "message": "Ushbu havola orqali botga o'ting va 'Start' tugmasini bosing."}, status=status.HTTP_200_OK
        )



class TelegramConfirmView(APIView):
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

        user = User.objects.filter(telegram_link_token=token).first()
        if not user:
            return Response(
                {"detail": "Havola eskirgan yoki token yaroqsiz."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        User.objects.filter(telegram_chat_id=chat_id).exclude(id=user.id).update(telegram_chat_id= None)


        user.telegram_chat_id = chat_id
        user.telegram_link_token = None
        user.save(update_fields=['telegram_chat_id', 'telegram_link_token'])


        return Response({
            "detail": "Hisobingiz muvaffaqiyatli bog'landi.",
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip()
        }, status=status.HTTP_200_OK)



class TelegramUserEventsView(APIView):
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

        registration = Registration.objects.filter(user=user, status=Registration.Status.CONFIRMED).select_related('event').order_by('event__start_at')

        events_data = [{
                "registration_id": reg.id,
                "event_title": reg.event.title,
                "event_type": reg.event.event_type,
                "location": reg.event.location,
                "start_at": reg.event.start_at.strftime('%Y-%m-%d %H:%M'),
                "status": reg.status,
            } for reg in registration
        ]

        return Response({
            "user_email": user.email,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "count": len(events_data),
            "events": events_data
        }, status=status.HTTP_200_OK)
        



        