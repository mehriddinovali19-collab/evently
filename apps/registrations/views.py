from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from .models import Registration
from .serializers import RegistrationSerializer, MyRegistrationSerializer
from .services import register_user_to_event, unregister_user_to_event

class RegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id: int):
        registration = register_user_to_event(user=request.user, event_id=event_id)
        serializer = RegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventUnregisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id: int):
        unregistertion = unregister_user_to_event(user=request.user, event_id=event_id)
        return Response({
            "detail": "Tadbirdan muvaffaqiyatli chiqdingiz.", "status": unregistertion.status
        }, status=status.HTTP_200_OK)

class MyRegistertionView(generics.ListAPIView):
    serializer_class = MyRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).select_related('event')



