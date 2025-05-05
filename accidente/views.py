from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer, AccidenteListSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated 
from django.db import DatabaseError 
from rest_framework import generics
from .models import Accidente
import traceback

class AccidenteCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        print("===== NUEVA SOLICITUD DE REGISTRO DE ACCIDENTE =====")
        print("Datos recibidos:", request.data)
        print("Usuario autenticado:", request.user)

        try:
            serializer = AccidenteSerializer(data=request.data)
            if serializer.is_valid():
                print("Serializer válido. Procediendo a guardar el accidente...")
                accidente = serializer.save(usuario=request.user)
                print("Accidente guardado con éxito:", accidente)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print("Errores de validación del serializer:", serializer.errors)
                return Response({
                    "CODE_ERR": "VALIDATION_ERROR",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except DatabaseError as e:
            print("Error al guardar en base de datos:", str(e))
            traceback.print_exc()
            return Response({"CODE_ERR": "DB_SAVE_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print("Excepción inesperada:", str(e))
            traceback.print_exc()
            return Response({
                "CODE_ERR": "SERVER_ERROR",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            'count': count,
            'accidentes': serializer.data
        })