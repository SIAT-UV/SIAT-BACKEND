from django.db import models

# Create your models here.
from django.db import models

class Ubicacion(models.Model):
    AREA = models.CharField(max_length=255, blank=True, null=True)
    DIRECCION_HECHO = models.CharField(max_length=255, blank=True, null=True)
    BARRIO_HECHO = models.CharField(max_length=255, blank=True, null=True)
    Cordenada_Geografica = models.CharField(max_length=255, blank=True, null=True)  # Como string

    def __str__(self):
        return f"{self.AREA} - {self.DIRECCION_HECHO}"

class Accidente(models.Model):
    AÑO = models.IntegerField()
    FECHA = models.DateField()
    DIA = models.CharField(max_length=20)
    HORA = models.TimeField()
    CONTROLES_DE_TRANSITO = models.CharField(max_length=255, blank=True, null=True)
    CLASE_DE_ACCIDENTE = models.CharField(max_length=100)
    CLASE_DE_SERVICIO = models.CharField(max_length=100)
    GRAVEDAD_DEL_ACCIDENTE = models.CharField(max_length=100)
    CLASE_DE_VEHICULO = models.CharField(max_length=100)

    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.FECHA} - {self.CLASE_DE_ACCIDENTE}"
    


