from django.contrib import admin
from import_export.admin import ImportExportMixin
from studio_app.models import Studio, Member, Membership


class StudioAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


class MemberAdmin(ImportExportMixin, admin.ModelAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'id', 'name', 'studio', 'get_status_display', 'created_by', 'created_at', 'updated_by', 'updated_at'
    )
    pass


class MembershipAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


admin.site.register(Studio, StudioAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Membership, MembershipAdmin)
