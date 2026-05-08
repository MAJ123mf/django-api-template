from django.contrib.gis import admin
from django.contrib import admin as django_admin  # ← dodaj
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Parcels, Parcels_Owners

class ParcelsAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 15.0806,
            'default_lat': 46.5044,
            'default_zoom': 14,
        }
    }

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    
    def get_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Skupine'

django_admin.site.unregister(User)
django_admin.site.register(User, CustomUserAdmin)

admin.site.register(Parcels_Owners, admin.ModelAdmin)
admin.site.register(Parcels, ParcelsAdmin)
