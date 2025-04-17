from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils import timezone
from .models import Usuario


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["cedula", "first_name", "last_name", "email", "password"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate_email(self, value):
        email = value.lower()
        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user

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

            
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = Usuario.objects.get(email=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con este correo electrónico.")
        user.generate_otp()
        send_mail(
            subject="Código de recuperación de contraseña",
            message=f"Tu código de recuperación es: {user.otp}",
            from_email="noreply@tudominio.com",
            recipient_list=[user.email],
        )
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        email = data.get("email").lower()
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado.")
        if user.otp != data.get("otp"):
            raise serializers.ValidationError("Código OTP inválido.")
        if user.otp_expiration < timezone.now():
            raise serializers.ValidationError("El código OTP ha expirado.")
        return data

    def save(self):
        user = Usuario.objects.get(email=self.validated_data["email"].lower())
        user.set_password(self.validated_data["new_password"])
        user.otp = None
        user.otp_expiration = None
        user.save()
        return user
