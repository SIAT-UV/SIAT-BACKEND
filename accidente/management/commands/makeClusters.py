import numpy as np
from django.core.management.base import BaseCommand
from sklearn.cluster import DBSCAN
from django.utils import timezone
from django.contrib.gis.geos import Point, GEOSGeometry
from accidente.models import Accidente, IntersectionCluster

class Command(BaseCommand):
    help = 'Detecta intersecciones (clusters) con mayor cantidad de accidentes usando DBSCAN'

    def handle(self, *args, **kwargs):
        # 1. Obtener accidentes confirmados con coordenadas definidas
        accidentes = list(Accidente.objects.filter(confirmado=True, coordenada_geografica__isnull=False))
        if not accidentes:
            self.stdout.write("No hay accidentes confirmados con coordenadas definidas.")
            return

        # 2. Extraer y reproyectar las coordenadas a EPSG:3857 (métrico)
        coords = []
        for acc in accidentes:
            # Crear una copia de la geometría usando WKB
            geom = GEOSGeometry(acc.coordenada_geografica.wkb)
            # Si no tiene SRID, asignarlo (asumimos 4326)
            if not geom.srid:
                geom.srid = 4326
            geom.transform(3857)  # Reproyectar a sistema métrico
            coords.append([geom.x, geom.y])
        coords = np.array(coords)

        # 3. Aplicar DBSCAN para agrupar accidentes
        # eps = 30 metros; min_samples define el número mínimo de accidentes para formar un cluster
        db = DBSCAN(eps=30, min_samples=2).fit(coords)
        labels = db.labels_

        # 4. Agrupar accidentes por etiqueta (ignorar ruido, label = -1)
        clusters = {}
        for label, coord in zip(labels, coords):
            if label == -1:
                continue
            clusters.setdefault(label, []).append(coord)

        # 5. Calcular el centroide y conteo de cada cluster
        intersection_clusters = []
        for label, pts in clusters.items():
            pts_arr = np.array(pts)
            centroid = pts_arr.mean(axis=0)
            count = len(pts)
            intersection_clusters.append((label, centroid, count))

        # 6. Limpiar clusters previos (opcional)
        IntersectionCluster.objects.all().delete()

        # 7. Guardar cada cluster (transformando el centroide a EPSG:4326)
        for label, centroid, count in intersection_clusters:
            pt = Point(centroid[0], centroid[1], srid=3857)
            pt.transform(4326)  # Convertir de nuevo a geográficas
            IntersectionCluster.objects.create(
                centroide=pt,
                accident_count=count,
                fecha_actualizacion=timezone.now()
            )

        self.stdout.write(f"Se han detectado y guardado {len(intersection_clusters)} intersecciones con accidentes.")
