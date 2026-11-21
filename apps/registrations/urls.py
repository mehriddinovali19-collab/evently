from django.urls import path
from .views import RegistrationView, MyRegistertionView, EventUnregisterView

urlpatterns = [
    path('events/<int:event_id>/register/', RegistrationView.as_view(), name='event-register'),
    path('events/<int:event_id>/unregister/', EventUnregisterView.as_view(), name='event-unregister'),
    path('me/registrations/', MyRegistertionView.as_view(), name='my-registrations'),
]