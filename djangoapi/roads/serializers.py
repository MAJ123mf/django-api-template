from django.db import connection
from rest_framework import serializers
from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Roads
from django.contrib.gis.geos import GEOSGeometry


class RoadsSerializer(GeoModelSerializer):
    check_geometry_is_valid = True
    matrix9IM = '1*T***T**'
    geoms_as_wkt = True
    check_st_relation = True

    class Meta:
        model = Roads
        fields = ['id', 'geom', 'geom_geojson', 'geom_wkt', 'str_name', 'administrator', 'maintainer', 'length']

    def create(self, validated_data):
        geom_wkb = validated_data.get('geom')
        instance = super().create(validated_data)
        if geom_wkb:
            geom = GEOSGeometry(geom_wkb)
            print(f"Izračunana dolžina (create): {geom.length}")
            instance.length = round(geom.length, 2)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        geom_wkb = validated_data.get('geom', None)
        instance = super().update(instance, validated_data)
        if geom_wkb:
            geom = GEOSGeometry(geom_wkb)
            print(f"Izračunana dolžina (update): {geom.length}")
            instance.length = round(geom.length, 2)
            instance.save()
        return instance

    def validate_geom(self, value):
        # Najprej pokliči parent validacijo
        value = super().validate_geom(value)

        # Nato preveri tip in veljavnost geometrije
        try:
            geom = GEOSGeometry(value)
        except Exception:
            raise serializers.ValidationError("Neveljavna geometrija.")

        if geom.geom_type != 'LineString':
            raise serializers.ValidationError("Geometrija mora biti tipa LineString.")

        if not geom.simple:
            raise serializers.ValidationError("Linija (cesta) ne sme sekati sama sebe.")

        return value
