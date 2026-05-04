from django.urls import path
from . import views

urlpatterns = [
    path("gpkg/", views.ExportGeoPackage.as_view(), name="export_geopackage"),  # ← .as_view()
]
