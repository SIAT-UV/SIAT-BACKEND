from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from .models import Usuario
from rest_framework_simplejwt.views import TokenObtainPairView


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
        token['cedula'] = user.cedula  # Agregar cedula al payload del token
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['id'] = user.cedula  # Usar cedula como "id" en la respuesta
        data['username'] = f"{user.first_name} {user.last_name}"
        return data


