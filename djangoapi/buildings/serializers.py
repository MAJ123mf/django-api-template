from django.db import connection

from rest_framework import serializers

from core.myLib.geoModelSerializer import GeoModelSerializer
from .models import Buildings, Owners

class BuildingsSerializer(GeoModelSerializer):
    check_geometry_is_valid = True
    check_st_relation = True
    matrix9IM = 'T********'
    geoms_as_wkt = True

    class Meta:
        model = Buildings
        fields = GeoModelSerializer.Meta.fields + ['sifko', 'st_stavbe', 'description', 'area']

    def validate_geom(self, value):
        print('validate_geom, child')
        return super().validate_geom(value)

    def create(self, validated_data):
        geom = validated_data.get('geom')
        if geom:
            with connection.cursor() as cursor:
                cursor.execute("SELECT ST_Area(%s)", [geom])
                row = cursor.fetchone()
                validated_data['area'] = round(row[0], 2) if row else 0
        return super().create(validated_data)

    def update(self, instance, validated_data):
        geom = validated_data.get('geom')
        if geom:
            with connection.cursor() as cursor:
                cursor.execute("SELECT ST_Area(%s)", [geom])
                row = cursor.fetchone()
                validated_data['area'] = round(row[0], 2) if row else 0
        return super().update(instance, validated_data)

        
class OwnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owners
        fields = ['id', 'name', 'dni']
    
    def validate_name(self, value):
        if 'bad' in value:
            raise serializers.ValidationError("The name can't contain 'bad'.")
        return value
