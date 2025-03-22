from rest_framework import serializers
from .models import Accidente, Ubicacion

class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = ('AREA', 'DIRECCION_HECHO', 'BARRIO_HECHO', 'coordenada_geografica')

class AccidenteSerializer(serializers.ModelSerializer):
    ubicacion = UbicacionSerializer()
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
            'ubicacion',
            'imagen',

        )

    def create(self, validated_data):
        # Extraer datos anidados de ubicación
        ubicacion_data = validated_data.pop('ubicacion', None)
        ubicacion = None
        if ubicacion_data:
            ubicacion = Ubicacion.objects.create(**ubicacion_data)
        accidente = Accidente.objects.create(ubicacion=ubicacion, **validated_data)
        return accidente
