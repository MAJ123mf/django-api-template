from django.urls import path
from .views import ConvertToGeoJSON

urlpatterns = [
    path('convert/', ConvertToGeoJSON.as_view(), name='convert_to_geojson'),
]