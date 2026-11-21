from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Event
from .serializers import EventSerializer
from .filters import EventFilter
from .permissions import IsAdminOrReadonly
from apps.users.permissions import IsAdmin

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


    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def close(self, request, pk=None):
        """POST /api/v1/events/{id}/close/                                                                                                                       
            Admin tadbirni muddatidan oldin yopishi uchun"""
        event = self.get_object()
        event.status = Event.Status.CLOSED
        event.save(update_fields=['status', 'updated_at'])
        return Response({"detail": "Tadbir muvaffaqiyatli yopildi.", 'status': event.status}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['get'], permission_classes=[IsAdmin], url_path='participants')
    def get_list_participants(self, request, pk=None):
        """GET /api/v1/events/{id}/participants/                                                                                                                 
            Admin tadbirga ro'yxatdan o'tgan qatnashchilar ro'yxatini ko'rishi uchun"""
        event = self.get_object()
        active_registers = event.registrations.filter(status='confirmed').select_related('user')
        data = [{
            "registration_id": r.id,
            "user_id": r.user.id,
            "full_name": f"{r.user.first_name} {r.user.last_name}".strip(),
            "email": r.user.email,
            "phone_number": r.user.phone_number,
            "registered_at": r.created_at,
        } for r in active_registers]

        return Response({"count":len(data), "result": data}, status=status.HTTP_200_OK)