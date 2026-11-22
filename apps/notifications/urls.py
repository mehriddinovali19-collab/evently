from django.urls import path
from .views import (
    TelegramLinkGenerateView,
    TelegramConfirmView,
    TelegramUserEventsView,
)

urlpatterns = [
    path('telegram/link/', TelegramLinkGenerateView.as_view(), name='telegram_link'),
    path('telegram/confirm/', TelegramConfirmView.as_view(), name='telegram_confirm'),
    path('telegram/my-events/', TelegramUserEventsView.as_view(), name='telegram_my_events'),
]