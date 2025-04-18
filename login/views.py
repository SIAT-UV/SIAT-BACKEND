from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistroUsuarioSerializer, CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework.views import APIView
from django.conf import settings
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from django.contrib.auth import get_user_model
import jwt 
import logging
from .models import Usuario

@api_view(['POST'])
def registro_api(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            # Configurar cookies con parámetros desde settings
            #self._set_access_cookie(response)
            self._set_refresh_cookie(response)
            
            # Limpiar tokens del cuerpo de respuesta
            self._clean_response_data(response)
            
            return response
            
        except AuthenticationFailed as e:
            return Response(
                {"CODE_ERR": "INVALID_CREDENTIALS"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(

                {"CODE_ERR": "AUTH_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    def _set_refresh_cookie(self, response):
        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        )

    def _clean_response_data(self, response):
        response.data.pop('refresh', None)    
        return response


logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get('refresh_token')
        if not refresh:
            return Response(
                {"CODE_ERR": "REFRESH_NO_PROVIDED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(
            data={'refresh': refresh},
            context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            logger.error(f"TokenError: {e}")
            return Response(
                {"CODE_ERR": "TOKEN_INVALIDO"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        tokens = serializer.validated_data 

        response = Response(status=status.HTTP_200_OK)
        #Seteamos nueva cookie de access
        """
        response.set_cookie(
            key='access_token',
            value=tokens['access'],
            httponly=True,
            secure=True,
            samesite='None',
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        )
        """
        # Seteamos nueva cookie de refresh
        if tokens.get('refresh'):
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True,
                samesite='None',
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            )

        try:
            payload = jwt.decode(tokens['access'], settings.SECRET_KEY, algorithms=['HS256'])
            user = Usuario.objects.get(cedula=payload['cedula'])
            response.data = {
                'access': tokens['access'],
                'user': {
                    'nombre': f"{user.first_name} {user.last_name}",
                    #'cedula': user.cedula
                }
            }
        except Exception as e:
            logger.error(f"DecodeError / UsuarioError: {e}")
            response({"CODE_ERR": "INTERNAL_SERVER_ERROR"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        return response

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Código OTP enviado al correo electrónico."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contraseña restablecida exitosamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        