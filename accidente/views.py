from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer, AccidenteListSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated 
from django.db import DatabaseError 
from rest_framework import generics
from .models import Accidente

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

class AccidenteListView(generics.ListAPIView):
    serializer_class = AccidenteListSerializer

    def get_queryset(self):
        # Filtrar solo los accidentes confirmados
        return Accidente.objects.filter(confirmado=True)

    def list(self, request, *args, **kwargs):
        """
        Sobrescribe el método `list` para incluir el conteo de accidentes
        confirmados en la respuesta.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # Contamos cuántos accidentes se están listando
        count = queryset.count()

        # Incluimos el conteo en la respuesta
        return Response({
            'Número de accidentes graficados': count,
            'accidentes': serializer.data
        })