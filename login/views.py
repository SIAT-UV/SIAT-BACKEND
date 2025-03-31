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
        response = super().post(request, *args, **kwargs)
        
        # Guardar access_token en cookie
        response.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=False,  # Desarrollo sin HTTPS
            samesite='Lax',
            max_age=15 * 60,
        )
        
        # Guardar refresh_token en cookie
        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=24 * 60 * 60,
        )
        
        # Eliminar tokens del cuerpo de la respuesta (quedan 'id' y 'username')
        del response.data['access']
        #del response.data['refresh']
        
        return response

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        data = request.data.copy()
        data['refresh'] = refresh_token  # Clave correcta: "refresh"
        
        try:
            response = super().post(request, data=data, *args, **kwargs)
        except Exception as e:
            return Response({"error": "Token inválido"}, status=401)
        
        if 'access' in response.data:
            access_token = response.data['access']
            try:
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                cedula = payload.get('cedula')  # Obtener cedula del payload
                user = Usuario.objects.get(cedula=cedula)
                
                # Agregar datos del usuario a la respuesta
                response.data['id'] = user.cedula
                response.data['username'] = f"{user.first_name} {user.last_name}"
                
                # Actualizar cookie del access_token
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=False,
                    samesite='Lax',
                    max_age=15 * 60,
                )
            except Usuario.DoesNotExist:
                return Response({"error": "Usuario no encontrado"}, status=404)
            except (jwt.ExpiredSignatureError, jwt.DecodeError):
                return Response({"error": "Token inválido"}, status=401)
        
        return response
    def post(self, request, *args, **kwargs):
        # Obtener refresh_token de la cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        # Crear una copia mutable de request.data y usar la clave correcta "refresh"
        data = request.data.copy()
        data['refresh'] = refresh_token  
        
        try:
            response = super().post(request, data=data, *args, **kwargs)
        except (InvalidToken, TokenError) as e:
            logger.error(f"Error al refrescar token: {e}")
            return Response({"error": "Token inválido"}, status=401)
        
        if 'access' in response.data:
            access_token = response.data['access']
            try:
                # Decodificar el token para obtener el user_id (clave correcta)
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                cedula = payload.get('cedula')  # ¡Clave correcta!
                user = User.objects.get(cedula=cedula)
                
                # Agregar datos del usuario a la respuesta
                response.data['cedula'] = user.cedula  # Ajusta según tu modelo
                response.data['username'] = f"{user.first_name} {user.last_name}"
                
                # Actualizar cookie del access_token
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=False,
                    samesite='Lax',
                    max_age=15 * 60,
                )
            except User.DoesNotExist:
                logger.error("Usuario no encontrado")
            except (jwt.ExpiredSignatureError, jwt.DecodeError) as e:
                logger.error(f"Error decodificando token: {e}")
        print(response.data)
        return response