from django.contrib.gis import admin
from .models import Buildings

class BuildingsAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 15.0806,
            'default_lat': 46.5044,
            'default_zoom': 14,
        }
    }
admin.site.register(Buildings, BuildingsAdmin)
