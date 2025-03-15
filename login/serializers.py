from rest_framework import serializers
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
