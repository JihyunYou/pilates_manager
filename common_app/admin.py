from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from import_export.admin import ImportExportMixin
from common_app.models import User


class CustomUserAdmin(ImportExportMixin, UserAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'get_user_type_display', 'name', 'email', 'employer', 'is_active', 'is_admin'
    )

    # 필터링 옵션 ( User Model의 경우 기본 것과 충돌나는 것이 있어 명시 필요 )
    list_filter = (
        'user_type', 'employer', 'is_active', 'is_admin'
    )

    # CHG
    fieldsets = (
        (
            '기본 정보', {
                'fields': ('email', 'name', 'password', 'user_type')
            }
        ),
        (
            '고용 정보', {
                'fields': ('employer', 'lesson_fee', 'employment_start_date', 'employment_end_date')
            }
        ),
        (
            '권한 설정', {
                'fields': ('is_active', 'is_admin')
            }
        )
    )

    # ADD
    add_fieldsets = (
        (
            '기본 정보', {
                'fields': ('email', 'name', 'password1', 'password2', 'user_type')
            }
        ),
        (
            '고용 정보', {
                'fields': ('employer', 'lesson_fee', 'employment_start_date', 'employment_end_date')
            }
        ),
        (
            '권한 설정', {
                'fields': ('is_active', 'is_admin')
            }
        )
    )

    ordering = ('user_type', 'name')


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)