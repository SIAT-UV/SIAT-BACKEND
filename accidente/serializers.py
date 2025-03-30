from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Accidente


class AccidenteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)  # Se asigna automáticamente
    imagen = serializers.ImageField(required=False)

    class Meta:
        model = Accidente
        fields = (
            'usuario',
            'FECHA',
            'HORA',
            'CONTROLES_DE_TRANSITO',
            'CLASE_DE_ACCIDENTE',
            'CLASE_DE_SERVICIO',
            'GRAVEDAD_DEL_ACCIDENTE',
            'CLASE_DE_VEHICULO',
            'AREA', 
            'DIRECCION_HECHO', 
            'BARRIO_HECHO', 
            'coordenada_geografica',
            'imagen',
        )

    def create(self, validated_data):
        # Crear el objeto Accidente directamente
        accidente = Accidente.objects.create(**validated_data)
        return accidente

