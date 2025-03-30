from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegistroUsuarioSerializer

@api_view(['POST'])
def registro_api(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario registrado correctamente"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Guardar access_token en cookie HttpOnly
        response.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=False,  # Cambiar a False sin HTTPS
            samesite='Lax',
            max_age=15 * 60,  # 15 minutos (coincide con ACCESS_TOKEN_LIFETIME)
        )
        
        # Guardar refresh_token en cookie HttpOnly (opcional)
        response.set_cookie(
            key='refresh_token',
            value=response.data['refresh'],
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=24 * 60 * 60,  # 1 día
        )
        
        # Eliminar tokens del cuerpo de la respuesta
        del response.data['access']
        del response.data['refresh']
        
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Obtener refresh_token de la cookie (no del body)
        refresh_token = request.COOKIES.get('refresh_token')
        request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        # Actualizar access_token en la cookie
        response.set_cookie(
            key='access_token',
            value=response.data['access'],
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=15 * 60,
        )
        return response

