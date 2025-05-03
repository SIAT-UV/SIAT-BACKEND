from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated 
from django.db import DatabaseError 

class AccidenteCreateView(APIView):
    # vista protegida
    permission_classes = [IsAuthenticated]
    # Se especifica que la vista acepta archivos y formularios
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, format=None):
        # Crear el serializer con los datos de la solicitud
        try:
            serializer = AccidenteSerializer(data=request.data)
            if serializer.is_valid():
                # Se asigna el usuario autenticado (instancia de Usuario)
                accidente = serializer.save(usuario=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # Si el serializer no es válido, se devuelven los errores, notificando que el usuario no ingreso los datos correctamente
        except DatabaseError as e:
            return Response({"CODE_ERR": "DB_SAVE_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Manejo de excepciones específicas
            return Response({"CODE_ERR": "SERVER_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"CODE_ERR": "Datos no ingresados correctamente"}, status=status.HTTP_400_BAD_REQUEST)


