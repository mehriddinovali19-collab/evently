from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegisterSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required= True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
            'role'
            )
        read_only_fields = ('id', 'role') 

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise ValueError("Password and Password conform do not match! ")
        return attrs


    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserMeSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'phone_number', 'role', 'telegram_chat_id', 'date_joined')
        read_only_fields = ('id', 'email', 'role', 'telegram_chat_id', 'date_joined')