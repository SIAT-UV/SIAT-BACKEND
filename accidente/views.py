from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer, AccidenteListSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated 
from django.db import DatabaseError 
from rest_framework import generics
from .models import Accidente
from SIAT.utils.email import send_email

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
                # Crear cuerpo del correo con los datos del accidente
                datos = serializer.validated_data
                cuerpo = f"""
                    Se ha registrado un nuevo accidente de tránsito con la siguiente información:

                    - Fecha: {datos.get('FECHA')}
                    - Hora: {datos.get('HORA')}
                    - Controles de Tránsito: {datos.get('CONTROLES_DE_TRANSITO')}
                    - Clase de Accidente: {datos.get('CLASE_DE_ACCIDENTE')}
                    - Clase de Servicio: {datos.get('CLASE_DE_SERVICIO')}
                    - Gravedad: {datos.get('GRAVEDAD_DEL_ACCIDENTE')}
                    - Vehículo: {datos.get('CLASE_DE_VEHICULO')}
                    - Área: {datos.get('AREA')}
                    - Dirección: {datos.get('DIRECCION_HECHO')}
                    - Barrio: {datos.get('BARRIO_HECHO')}
                    - Coordenadas: {datos.get('coordenada_geografica')}

                    Gracias por usar el sistema SIAT.
                    """
                # Correo del usuario autenticado
                correo_destino = request.user.email
                send_email("Confirmación de Registro de Accidente", cuerpo, correo_destino)


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
            'count': count,
            'accidentes': serializer.data
        })