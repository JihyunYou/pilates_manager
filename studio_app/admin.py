from django.contrib import admin
from import_export.admin import ImportExportMixin
from studio_app.models import Studio


class StudioAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


admin.site.register(Studio, StudioAdmin)
