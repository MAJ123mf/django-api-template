import subprocess
import os
import tempfile
from django.http import FileResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ExportGeoPackage(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Izvozi GeoPackage",
        operation_description="Ustvari GeoPackage s štirimi sloji (parcele, stavbe, ceste, naslovi) in ga ponudi za prenos.",
        responses={
            200: openapi.Response(description="GeoPackage datoteka"),
            403: openapi.Response(description="Dostop zavrnjen"),
            500: openapi.Response(description="Napaka pri izvozu")
        }
    )
    def get(self, request):
        """
        Ustvari GeoPackage s štirimi sloji (parcele, stavbe, ceste, naslovi)
        in ga ponudi za prenos uporabniku.
        """
        # Preveri, ali ima uporabnik pravico za izvoz
        if not request.user.has_perm('export.can_export_geopackage'):
            raise PermissionDenied("Nimaš pravice za izvoz podatkov.")

        db_conn = (
            f"PG:dbname={settings.DATABASES['default']['NAME']} "
            f"user={settings.DATABASES['default']['USER']} "
            f"password={settings.DATABASES['default']['PASSWORD']} "
            f"host={settings.DATABASES['default']['HOST']} "
            f"port={settings.DATABASES['default']['PORT']}"
        )

        layers = ["parcels_parcels", "buildings_buildings", "roads_roads", "addresses_addresses"]

        tmp = tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False)
        output_path = tmp.name
        tmp.close()

        if os.path.exists(output_path):
            os.remove(output_path)

        for i, layer in enumerate(layers):
            cmd = [
                "ogr2ogr",
                "-f", "GPKG",
                output_path,
                db_conn,
                layer,
            ]
            if i > 0:
                cmd += ["-update", "-append"]

            subprocess.run(cmd, check=True)

        return FileResponse(open(output_path, "rb"), as_attachment=True, filename="podatki.gpkg")
