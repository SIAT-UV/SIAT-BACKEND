from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class AccidenteCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, format=None):

                # Verificar si el header Authorization está presente
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(
                {"CODE_ERR": "AUTHORIZATION_HEADER_MISSING"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar si el token comienza con 'Bearer '
        auth_header = request.META['HTTP_AUTHORIZATION']
        if not auth_header.startswith('Bearer '):
            return Response(
                {"CODE_ERR": "INVALID_TOKEN_FORMAT"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            return Response(
                {"CODE_ERR": "INVALID_CREDENTIALS"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Crear el serializer con los datos de la solicitud
        serializer = AccidenteSerializer(data=request.data)
        if serializer.is_valid():
            # Se asigna el usuario autenticado (instancia de Usuario)
            accidente = serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Si el serializer no es válido, se devuelven los errores, notificando que el usuario no ingreso los datos correctamente
        return Response({"CODE_ERR": "Datos no ingresados correctamente"}, status=status.HTTP_400_BAD_REQUEST)



