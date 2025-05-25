from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistroUsuarioSerializer, CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework.views import APIView
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
import jwt 
import logging
from .models import Usuario
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def registro_api(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access_token = str(refresh.access_token)

        response_data = {
            "access": access_token,
            "username": f"{user.first_name} {user.last_name}",
        }
        
        response = Response(response_data, status=status.HTTP_201_CREATED)
        
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        )
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
            response = super().post(request, *args, **kwargs)

            # Configurar cookies con parámetros desde settings
            #self._set_access_cookie(response)
            self._set_refresh_cookie(response)
            
            # Limpiar tokens del cuerpo de respuesta
            self._clean_response_data(response)
            return response
            
    def _set_refresh_cookie(self, response):
        if 'refresh' in response.data:
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
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
            )

        try:
            payload = jwt.decode(tokens['access'], settings.SECRET_KEY, algorithms=['HS256'])
            user = Usuario.objects.get(cedula=payload['cedula'])
            response.data = {
                'access': tokens['access'],
                'username': f"{user.first_name} {user.last_name}",
                    #'cedula': user.cedula
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

# Vista para cerrar sesión

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            if refresh_token is None:
                return Response({"error": "No se proporcionó token de actualización"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklisteamos el token

            response = Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            

            return response

        except TokenError as e:
            logger.error(f"TokenError al intentar blacklistear: {e}")
            return Response({"error": "Token inválido o ya expirado"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(f"Error inesperado al hacer logout: {e}")
            return Response({"error": "Error al cerrar sesión"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getDataUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            auth_header = request.headers.get('Authorization', '').split()
            if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
                return Response(
                    {"CODE_ERR": "INVALID_TOKEN"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            token = auth_header[1]
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,  # Clave secreta de Django
                algorithms=['HS256']
            )
            cedula_usuario = payload.get('cedula')
            if not cedula_usuario:
                return Response(
                    {"CODE_ERR": "INVALID_TOKEN"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            usuario = Usuario.objects.get(cedula=cedula_usuario)
            data = usuario.get_data()
            return Response(data, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"CODE_ERR": "ACCESS_TOKEN_EXPIRED"},
                status=status.HTTP_403_FORBIDDEN
            )
        except jwt.DecodeError:
            return Response(
                {"CODE_ERR": "INVALID_TOKEN"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Usuario.DoesNotExist:
            return Response(
                {"CODE_ERR": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f"Error inesperado: {e}")
            return Response(
                {"CODE_ERR": "INTERNAL_SERVER_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )