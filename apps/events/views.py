from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Event
from .serializers import EventSerializer
from .filters import EventFilter
from .permissions import IsAdminOrReadonly

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadonly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_at', 'created_at', 'title']
    ordering = ['-start_at']

    def get_queryset(self):
        """
        N+1 muammosini yo'qotish uchun:
        - select_related('created_by'): muallif ma'lumotlarini bitta JOIN bilan tortadi
        - annotate(registered_count=...): tasdiqlangan ro'yxatdan o'tganlar sonini SQL COUNT orqali hisoblaydi
        """
        return Event.objects.select_related('created_by').annotate(
            registered_count = Count(
                'registrations',
                filter=Q(registrations__status='confirmed') | Q(registrations__status='active'), distinct=True
            )
        )
        

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)