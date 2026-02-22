from django.urls import path
from . import views

urlpatterns = [
    path("gpkg/", views.export_geopackage, name="export_geopackage"),    # servis bo na voljo na naslovu: http://localhost:8000/export/gpkg/
]