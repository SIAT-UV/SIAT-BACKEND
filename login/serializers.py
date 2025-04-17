from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.hashers import make_password
from .models import Usuario


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["cedula", "first_name", "last_name", "email", "password"]

    # Encriptar la contraseña antes de guardarla
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        #token['username'] = f"{user.first_name} {user.last_name}"
        token['cedula'] = user.cedula  # Agregar cedula al payload del token
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        #data['id'] = user.cedula  # Usar cedula como "id" en la respuesta
        data['username'] = f"{user.first_name} {user.last_name}"
        return data

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def __init__(self, *args, **kwargs):
        data = kwargs.get('data', {})
        # Si no hay 'refresh' en body, lo tomamos de la cookie
        if 'refresh' not in data:
            request = kwargs['context']['request']
            data = data.copy()
            data['refresh'] = request.COOKIES.get('refresh_token')
            kwargs['data'] = data
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        # Validar que realmente exista en la cookie
        if not attrs.get('refresh'):
            raise InvalidToken('No refresh token cookie set')
        return super().validate(attrs)
