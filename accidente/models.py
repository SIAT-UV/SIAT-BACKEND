import locale
from cloudinary.models import CloudinaryField
from django.db import models
from SIAT import settings
from django.contrib.gis.db import models as geomodels

# Create your models here.


class Ubicacion(models.Model):
    AREA = models.CharField(max_length=255, blank=True, null=True)
    DIRECCION_HECHO = models.CharField(max_length=255, blank=True, null=True)
    BARRIO_HECHO = models.CharField(max_length=255, blank=True, null=True)
    coordenada_geografica = geomodels.PointField(geography=True, blank=True, null=True)

    def __str__(self):
        return f"{self.AREA} - {self.DIRECCION_HECHO}"

class Accidente(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, blank=True  
    )
    AÑO = models.IntegerField(editable=False)
    FECHA = models.DateField()
    DIA = models.CharField(max_length=20, editable=False)
    HORA = models.TimeField(null=True, blank=True)
    CONTROLES_DE_TRANSITO = models.CharField(max_length=255, blank=True, null=True)
    CLASE_DE_ACCIDENTE = models.CharField(max_length=100)
    CLASE_DE_SERVICIO = models.CharField(max_length=100)
    GRAVEDAD_DEL_ACCIDENTE = models.CharField(max_length=100)
    CLASE_DE_VEHICULO = models.CharField(max_length=100)

    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, null=True, blank=True)
    imagen = CloudinaryField('image', blank=True, null=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        if self.FECHA:
            self.AÑO = self.FECHA.year
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8') 
            self.DIA = self.FECHA.strftime('%A').capitalize()  
        super().save(*args, **kwargs)

        if self.total_aprobaciones() >= 5:
            self.confirmado = True

    def total_aprobaciones(self):
        return self.aprobaciones.count()

    def es_aprobado(self):
        return self.confirmado  

    def __str__(self):
        return f"{self.FECHA} - {self.CLASE_DE_ACCIDENTE} - Aprobaciones: {self.total_aprobaciones()}"
    
class Aprobaciones(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accidente = models.ForeignKey(Accidente, on_delete=models.CASCADE, related_name="aprobaciones")
    fecha_aprobacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'accidente') 

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.accidente.total_aprobaciones() >= 5:
            self.accidente.confirmado = True
            self.accidente.save()
    


