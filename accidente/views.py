from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccidenteSerializer, AccidenteListSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated 
from django.db import DatabaseError 
from rest_framework import generics
from .models import Accidente, Aprobaciones
from SIAT.utils.email import send_email
from django.conf import settings
from django.db import IntegrityError
import jwt
from django.contrib.auth import get_user_model

Usuario = get_user_model()

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
class AccidenteListViewGravity(generics.ListAPIView):
    serializer_class = AccidenteListSerializer

    def get_queryset(self):
        # Filtrar solo los accidentes confirmados
        queryset = Accidente.objects.filter(confirmado=True)
        gravedad = self.request.query_params.get('gravedad')
        if gravedad:
            queryset = queryset.filter(GRAVEDAD_DEL_ACCIDENTE__iexact=gravedad)
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Sobrescribe el método `list` para incluir el conteo de accidentes
        confirmados en la respuesta y mostrar la gravedad si se aplica un filtro.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()

        # Armar la respuesta
        response_data = {
            'count': count,
            'accidentes': serializer.data
        }

        # Si se aplicó un filtro de gravedad, incluirlo en la respuesta
        gravedad = request.query_params.get('gravedad')
        if gravedad:
            response_data['gravedad'] = gravedad.upper()

        return Response(response_data)   
     
# vista para aprobar un accidente mediante el id del accidente
class AprobarAccidenteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        try:
            # 1. Extraer usuario del token JWT
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
            # 2. Verificar si el usuario ya aprobó el accidente
            accidente = Accidente.objects.get(pk=pk)
            
            if Aprobaciones.objects.filter(usuario=usuario, accidente=accidente).exists():
                return Response(
                    {"CODE_ERR": "ALREADY_APPROVED"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3.1 Verificar si el accidente ya está aprobado

            if accidente.confirmado:
                return Response(
                    {"CODE_ERR": "ACCIDENT_ALREADY_CONFIRMED"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3.2 Crear aprobación
            Aprobaciones.objects.create(usuario=usuario, accidente=accidente)
            
            return Response(
                {"message": "Accidente aprobado exitosamente"},
                status=status.HTTP_201_CREATED
            )

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
        except Accidente.DoesNotExist:
            return Response(
                {"CODE_ERR": "ACCIDENT_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Usuario.DoesNotExist:
            return Response(
                {"CODE_ERR": "INVALID_USER"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except IntegrityError:
            return Response(
                {"CODE_ERR": "ALREADY_APPROVED"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"CODE_ERR": "INTERNAL_SERVER_ERROR"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    