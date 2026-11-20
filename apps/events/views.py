from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer
from .permissions import IsAdminOrReadonly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadonly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)