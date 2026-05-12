from django.db import models

class ExportPermission(models.Model):
    """Proxy model samo za namen definiranja custom pravice."""
    class Meta:
        managed = False          # Django ne ustvari tabele v bazi
        default_permissions = () # odstranim default add/change/delete/view
        permissions = [
            ("can_export_geopackage", "Can export GeoPackage"),
        ]
