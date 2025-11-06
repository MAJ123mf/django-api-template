
import subprocess
import os
import tempfile
from django.http import FileResponse
from django.conf import settings
from django.shortcuts import render

def export_geopackage(request):
    """
    Ustvari GeoPackage s štirimi sloji (parcele, stavbe, ceste, naslovi)
    in ga ponudi za prenos uporabniku.
    """

    # Nastavimo povezavo na PostGIS bazo (vzeto iz settings.py)
    db_conn = (
        f"PG:dbname={settings.DATABASES['default']['NAME']} "
        f"user={settings.DATABASES['default']['USER']} "
        f"password={settings.DATABASES['default']['PASSWORD']} "
        f"host={settings.DATABASES['default']['HOST']} "
        f"port={settings.DATABASES['default']['PORT']}"
    )

    # Imena slojev, kot jih imaš v PostGIS (tabela = ime sloja)
    layers = ["parcels_parcels", "buildings_buildings", "roads_roads", "addresses_addresses"]

    # Ustvari začasno datoteko
    tmp = tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False)
    output_path = tmp.name

    # Če slučajno obstaja, zbrišemo
    if os.path.exists(output_path):
        os.remove(output_path)

    # Ustvarimo GeoPackage in vanj dodamo vse 4 sloje
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

        # Reprojeciramo v WGS84 (če želiš)
        # cmd += ["-t_srs", "EPSG:4326"]

        subprocess.run(cmd, check=True)

    # Pošljemo datoteko uporabniku
    return FileResponse(open(output_path, "rb"), as_attachment=True, filename="podatki.gpkg")

