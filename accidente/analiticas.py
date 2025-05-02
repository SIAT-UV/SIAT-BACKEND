from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Accidente
from datetime import datetime
from .serializers import AccidenteSerializer
from rest_framework import status

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
        
        return Response({
            "count": accidentes.count(),
            "mes": fecha.month,
            "año": fecha.year,
            "resultados": serializer.data
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
            accidentes = Accidente.objects.filter(
                confirmado=True
            ).order_by('-FECHA')[:3]
            
            serializer = AccidenteSerializer(accidentes, many=True)
            
            #solo dejamos los campos: fecha + hora, BARRIO_HECHO, CLASE_DE_ACCIDENTE, CLASE_DE_SERVICIO, GRAVEDAD_DEL_ACCIDENTE
            for item in serializer.data:
                item.pop('usuario', None)
                item.pop('CONTROLES_DE_TRANSITO', None)
                item.pop('CLASE_DE_VEHICULO', None)
                item.pop('coordenada_geografica', None)
                item.pop('DIRECCION_HECHO', None)
                item.pop('imagen', None)
                item.pop('AREA', None)
                #quitamos fecha y hora y la agregamos como un solo campo
                item['fecha_hora'] = f"{item['FECHA']} {item['HORA']}"
                item.pop('FECHA', None)
                item.pop('HORA', None)
                
            return Response({
                "results": serializer.data
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
            
            return Response({
                "count": queryset.count(),
                "results": serializer.data
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
            
            return Response({
                "count": queryset.count(),
                "results": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

