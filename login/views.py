from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistroUsuarioSerializer, CustomTokenObtainPairSerializer
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
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
        except Exception as e:
            return Response({"CODE_ERR": "No existe el usuario"}, status=401)
        # Guardar access_token en cookie
        """
        response.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=False,  # Desarrollo sin HTTPS
            samesite='Lax',
            max_age=15 * 60,
        )
        """
        # Guardar refresh_token en cookie
        # En CustomTokenObtainPairView
        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        )
        
        # Eliminar tokens del cuerpo de la respuesta (queda 'username')
        #del response.data['access']
        del response.data['refresh']
        
        return response

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {"CODE_ERR": "REFRESH_TOKEN_REQUIRED"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        data = {'refresh': refresh_token}
        
        try:
            response = super().post(request, data=data, *args, **kwargs)
            
            if 'access' in response.data:
                access_token = response.data['access']
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                
                # Obtener usuario
                cedula = payload.get('cedula')
                user = Usuario.objects.get(cedula=cedula)
                print(user.get_full_name())

                # Limpiar tokens del cuerpo
                #del response.data['access']
                
                # Agregar datos de usuario
                response.data['user'] = {
                    #'cedula': user.cedula,
                    'username': f"{user.first_name} {user.last_name}"
                }
                
                # Actualizar cookies access
                """
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],  # True en producción
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                )
                """

                # Rotar refresh token si está configurado
                new_refresh_token = response.data.get('refresh')
                if new_refresh_token:
                    response.set_cookie(
                    key='refresh_token',
                    value=response.data['refresh'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                    )
                # Limpiar refresh token del cuerpo
                    if 'refresh' in response.data:
                        del response.data['refresh']
            return response
        # Manejo de errores:

        #excepcion si el token es blacklisted
        except InvalidToken:
            logger.error("Token inválido")
            return Response(
                {"CODE_ERR": "INVALID_TOKEN"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        except jwt.ExpiredSignatureError:
            logger.error("Refresh token expirado")
            return Response(
                {"CODE_ERR": "REFRESH_TOKEN_EXPIRED"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
            
        except jwt.DecodeError:
            logger.error("Error de decodificacion")
            return Response(
                {"CODE_ERR": "DECODE_ERROR"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Usuario.DoesNotExist:
            print("Usuario no encontrado")
            logger.error("Usuario no encontrado")
            return Response(
                {"CODE_ERR": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Exception as e:
            logger.critical(f"Error inesperado: {str(e)}")
            return Response(
                {"CODE_ERR": "SERVER_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )