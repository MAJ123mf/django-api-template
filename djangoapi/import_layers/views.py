from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import tempfile
import os
import json


class ConvertToGeoJSON(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Uvozi prostorsko datoteko",
        operation_description="Pretvori .gpkg, .shp, .kml ali .geojson v GeoJSON (EPSG:4326).",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Prostorska datoteka (.gpkg, .shp, .dbf, .prj, .shx, .kml, .geojson)"
            )
        ],
        responses={
            200: openapi.Response(description="GeoJSON FeatureCollection"),
            400: openapi.Response(description="Napaka v vhodni datoteki"),
            500: openapi.Response(description="Napaka pri konverziji")
        }
    )
    
    def post(self, request):
        uploaded_files = request.FILES.getlist('file')
        if not uploaded_files:
            return Response({'error': 'Ni datoteke'}, status=status.HTTP_400_BAD_REQUEST)

        tmp_dir = tempfile.mkdtemp()

        try:
            from osgeo import ogr, osr

            shp_path = None

            # Shrani vse datoteke v isto temp mapo
            for uploaded in uploaded_files:
                tmp_path = os.path.join(tmp_dir, uploaded.name)
                with open(tmp_path, 'wb') as f:
                    for chunk in uploaded.chunks():
                        f.write(chunk)
                if uploaded.name.endswith('.shp') or uploaded.name.endswith('.gpkg') or \
                   uploaded.name.endswith('.kml') or uploaded.name.endswith('.geojson'):
                    shp_path = tmp_path

            if not shp_path:
                return Response({'error': 'Ni .shp, .gpkg, .kml ali .geojson datoteke'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            datasource = ogr.Open(shp_path)
            if not datasource:
                return Response({'error': 'OGR ne more odpreti datoteke'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            layer = datasource.GetLayer(0)
            source_srs = layer.GetSpatialRef()
            target_srs = osr.SpatialReference()
            target_srs.ImportFromEPSG(3794)
            target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

            features = []

            if source_srs:
                transform = osr.CoordinateTransformation(source_srs, target_srs)
            else:
                # Ni .prj — predpostavi EPSG:3794
                src_srs = osr.SpatialReference()
                src_srs.ImportFromEPSG(3794)
                src_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                transform = osr.CoordinateTransformation(src_srs, target_srs)

            for feature in layer:
                geom = feature.GetGeometryRef()
                if geom:
                    geom.Transform(transform)
                props = {}
                for i in range(feature.GetFieldCount()):
                    props[feature.GetFieldDefnRef(i).GetName()] = feature.GetField(i)
                features.append({
                    'type': 'Feature',
                    'geometry': json.loads(geom.ExportToJson()) if geom else None,
                    'properties': props
                })

            return Response({'type': 'FeatureCollection', 'features': features})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            for f in os.listdir(tmp_dir):
                os.unlink(os.path.join(tmp_dir, f))
            os.rmdir(tmp_dir)
