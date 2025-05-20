from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Accidente
from datetime import datetime
from .serializers import AccidenteSerializer
from rest_framework import status
import jwt 
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser


def serialize_accidentes(data):
    serialized = []
    for item in data:
        item_copy = item.copy()
        item_copy.pop('usuario', None)
        item_copy.pop('CONTROLES_DE_TRANSITO', None)
        item_copy.pop('CLASE_DE_SERVICIO', None)
        item_copy.pop('coordenada_geografica', None)
        item_copy.pop('DIRECCION_HECHO', None)
        item_copy.pop('imagen', None)
        item_copy.pop('AREA', None)
        #item_copy['fecha_hora'] = f"{item_copy.pop('FECHA', '')} {item_copy.pop('HORA', '')}"
        serialized.append(item_copy)
    return serialized

class FilterAccidentByMonthView(APIView):
    def get(self, request):
        fecha_str = request.GET.get('fecha')  # Obtener la fecha del request
        fecha_str = fecha_str+"-01"
        if not fecha_str:
            return Response(
                {"error": "Parámetro 'fecha' requerido (formato: YYYY-MM-DD)"},
                status=400
            )
        
        try:
            # Convertir el string a objeto date
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=400
            )
        
        # Filtrar por mes y año de la fecha proporcionada
        accidentes = Accidente.objects.filter(
            confirmado=True,
            FECHA__year=fecha.year,
            FECHA__month=fecha.month
        )
        
        serializer = AccidenteSerializer(accidentes, many=True)
        
        resultado = serialize_accidentes(serializer.data) 

        return Response({
            "count": accidentes.count(),
            "mes": fecha.month,
            "año": fecha.year,
            "resultados": resultado
        })
    
# NUMERO DE ACCIDENTES POR MES
class CountAccidentByMonthView(APIView):
    def get(self, request):
        fecha_str = request.GET.get('fecha')
        fecha_str = fecha_str+"-01" 
        if not fecha_str:
            return Response(
                {"error": "Parámetro 'fecha' requerido (formato: YYYY-MM-DD)"},
                status=400
            )
        
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=400
            )
        
        conteo = Accidente.objects.filter(
            confirmado=True,
            FECHA__year=fecha.year,
            FECHA__month=fecha.month
        ).count()  
        
        return Response({
            "mes": fecha.month,
            "año": fecha.year,
            "total_accidentes": conteo
        })

class RecentlyAccidentView(APIView):
    def get(self, request):
        try:
            # Obtener los últimos 3 accidentes confirmados
            accidentes = Accidente.objects.filter(confirmado=True).order_by('-FECHA')[:3]
            
            serializer = AccidenteSerializer(accidentes, many=True)
            
            #solo dejamos los campos:
            # Fecha + hora, lugar, tipo de accidente, tipo de vehículo, gravedad

            resultado = serialize_accidentes(serializer.data) 

            return Response({
                "results": resultado
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al obtener accidentes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FilterAccidentByTypeView(APIView):
    def get(self, request):
        clase_accidente = request.GET.get('clase_de_accidente')
        
        if not clase_accidente:
            return Response(
                {"error": "Parámetro 'clase_de_accidente' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            queryset = Accidente.objects.filter(
                confirmado=True,
                CLASE_DE_ACCIDENTE__iexact=clase_accidente
            )
            serializer = AccidenteSerializer(queryset, many=True)
            resultado = serialize_accidentes(serializer.data) 
            
            return Response({
                "count": queryset.count(),
                "results": resultado
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FilterAccidentByTypeServiceView(APIView):
    def get(self, request):
        clase_servicio = request.GET.get('clase_de_servicio')
        
        if not clase_servicio:
            return Response(
                {"error": "Parámetro 'clase_de_servicio' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            queryset = Accidente.objects.filter(
                confirmado=True,
                CLASE_DE_SERVICIO__iexact=clase_servicio
            )
            serializer = AccidenteSerializer(queryset, many=True)
            resultado = serialize_accidentes(serializer.data) 
            
            return Response({
                "count": queryset.count(),
                "results": resultado
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class FilterSeverityOfTheAccidentView(APIView):
    def get(self, request):
        gravedad_accidente = request.GET.get('gravedad_del_accidente')
        
        if not gravedad_accidente:
            return Response(
                {"error": "Parámetro 'gravedad_del_accidente' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            queryset = Accidente.objects.filter(
                confirmado=True,
                CLASE_DE_SERVICIO__iexact=gravedad_accidente
            )
            serializer = AccidenteSerializer(queryset, many=True)
            resultado = serialize_accidentes(serializer.data) 
            
            return Response({
                "count": queryset.count(),
                "results": resultado
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AccidentsByUserView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return Response(
                    {"CODE_ERR": "INVALID_HEADER", "detail": "Encabezado de autorización inválido."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            token = auth_header.split(' ')[1]

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            cedula = payload.get('cedula')

            if not cedula:
                return Response(
                    {"CODE_ERR": "CEDULA_NOT_FOUND", "detail": "La cédula no está presente en el token."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except jwt.ExpiredSignatureError:
            return Response(
                {"CODE_ERR": "TOKEN_EXPIRED", "detail": "El token ha expirado."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError:
            return Response(
                {"CODE_ERR": "INVALID_TOKEN", "detail": "Token inválido."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {"CODE_ERR": "TOKEN_ERROR", "detail": f"Error al decodificar el token: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            queryset = Accidente.objects.filter(
                usuario__cedula=cedula
            )
            serializer = AccidenteSerializer(queryset, many=True)

            results = serialize_accidentes(serializer.data) 
            #results = serializer.data
            return Response({
                "total de accidentes": queryset.count(),
                "resultado": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"CODE_ERR": "SERVER_ERROR", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AccidentByYear(APIView):
    def get(self, request):
        year = request.GET.get('year')
        if not year:
            return Response(
                {"error": "Parámetro 'year' requerido (formato: YYYY)"},
                status=400
            )
        
        try:
            # Convertir el string a objeto date
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Formato de año inválido. Use YYYY."},
                status=400
            )
        
        # Filtrar por mes y año de la fecha proporcionada
        numAccidentes = Accidente.objects.filter(
            confirmado=True,
            FECHA__year=year
        ).count()
      

        return Response({
            "Total de accidentes": numAccidentes,
            "año": year
        })

class AccidentByDateRange(APIView):
    def get(self, request):
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            return Response(
                {"CODE_ERR": "Parámetros_'start_date'_y_'end_date'_son requeridos(formato: YYYY-MM-DD)"},
                status=400
            )
        
        try:
            # Convertir los strings a objetos date
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=400
            )
        
        # Filtrar por rango de fechas
        accidentes = Accidente.objects.filter(
            #confirmado=True,
            FECHA__range=(start_date, end_date)
        )
        
        serializer = AccidenteSerializer(accidentes, many=True)
        
        resultado = serialize_accidentes(serializer.data) 

        return Response({
            "count": accidentes.count(),
            "resultados": resultado
        })
class AccidentNoConfirmed(APIView):
    def get(self, request):
        try:
            accidentes = Accidente.objects.filter(
                confirmado=False
            ).order_by('-FECHA')
            serializer = AccidenteSerializer(accidentes, many=True)
            resultado = serialize_accidentes(serializer.data) 

            return Response({
                "results": resultado
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al obtener accidentes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )