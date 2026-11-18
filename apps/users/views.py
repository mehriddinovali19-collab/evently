from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializers, UserMeSerializers

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializers
    permission_classes = [permissions.AllowAny]


class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializers
    permission_classes = [permissions.IsAuthenticated]


    def get_object(self):
        return self.request.user