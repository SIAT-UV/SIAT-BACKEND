from rest_framework.views import APIView
from rest_framework.response import Response
from accidente.models import IntersectionCluster, Accidente
from django.contrib.gis.db.models.functions import Distance

## En esta vista se muestran las intersecciones con mayor cantidad de accidentes, buscamos las 3 intersecciones con mayor cantidad de accidentes y se muestran en el mapa, y se elige la direccion del accidente mas cercano al centroide

class ShowHighRiskView(APIView):
    def get(self, request, format=None):
        clusters = IntersectionCluster.objects.order_by("-accident_count")[:3]
        resultados = []

        for cluster in clusters:
            accidente = (Accidente.objects
                         .filter(confirmado=True, coordenada_geografica__isnull=False)
                         .annotate(distance=Distance('coordenada_geografica', cluster.centroide))
                         .order_by('distance')
                         .first())
            direccion = accidente.DIRECCION_HECHO if accidente and accidente.DIRECCION_HECHO else ""
            barrio = accidente.BARRIO_HECHO if accidente and accidente.BARRIO_HECHO else ""

            resultados.append({
                "centroide": {
                    "lat": cluster.centroide.y,  
                    "lon": cluster.centroide.x,
                },
                "accident_count": cluster.accident_count,
                "direccion": direccion,
                "barrio": barrio,
            })
        return Response(resultados)


    

