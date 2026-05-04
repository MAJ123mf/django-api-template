from django.contrib.gis import admin
from .models import Parcels, Parcels_Owners

class ParcelsAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 15.0806,
            'default_lat': 46.5044,
            'default_zoom': 14,
        }
    }
admin.site.register(Parcels_Owners, admin.ModelAdmin)
admin.site.register(Parcels, ParcelsAdmin)
