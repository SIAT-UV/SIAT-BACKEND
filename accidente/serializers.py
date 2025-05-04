from rest_framework import serializers
from .models import Accidente
from django.conf import settings
import googlemaps
from django.contrib.gis.geos import Point

class AccidenteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)  # Se asigna automáticamente
    imagen = serializers.ImageField(required=False)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)

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
            'lat',
            'lng',
        )
    def create(self, validated_data):
        lat = validated_data.pop('lat', None)
        lng = validated_data.pop('lng', None)

        if lat is not None and lng is not None:
            punto = Point(lng, lat)
        else:
            direccion = validated_data.get('DIRECCION_HECHO')
            if not direccion:
                raise serializers.ValidationError("Debe proporcionar una dirección si no hay coordenadas.")

            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            geocode_result = gmaps.geocode(direccion)

            if not geocode_result:
                raise serializers.ValidationError("No se pudo geolocalizar la dirección.")

            location = geocode_result[0]['geometry']['location']
            punto = Point(location['lng'], location['lat'])

        validated_data['coordenada_geografica'] = punto
        return Accidente.objects.create(**validated_data)
    
class AccidenteListSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()  # Latitud calculada
    lon = serializers.SerializerMethodField()  # Longitud calculada

    class Meta:
        model = Accidente
        fields = ('lat', 'lon')

    def get_lat(self, obj):
        if obj.coordenada_geografica:
            return obj.coordenada_geografica.y
        return None

    def get_lon(self, obj):
        if obj.coordenada_geografica:
            return obj.coordenada_geografica.x
        return None

    

