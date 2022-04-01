from django.contrib import admin
from django.db.models import Q
from import_export.admin import ImportExportMixin

from common_app.models import User
from studio_app.models import Studio, Member, Membership, MemberDefaultSchedule


# 지점 정보 Admin Page 설정
class StudioAdmin(ImportExportMixin, admin.ModelAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'id', 'name', 'owner', 'address', 'get_teachers', 'created_by', 'created_at', 'updated_by', 'updated_at'
    )

    fieldsets = (
        (
            '기본 정보', {'fields': ('name', 'owner', 'address')}
        ),
        (
            '소속 강사', {'fields': ('teachers',)}
        ),
        (
            '작성자', {'fields': ('created_by', 'updated_by')}
        )
    )

    def get_teachers(self, obj):
        return ', '.join([teacher.name for teacher in obj.teachers.all()])

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['owner'].queryset = User.objects.filter(user_type__lte=2)
        context['adminform'].form.fields['teachers'].queryset = User.objects.filter(Q(user_type=2) | Q(user_type=3))
        return super(StudioAdmin, self).render_change_form(request, context, *args, **kwargs)


class MemberAdmin(ImportExportMixin, admin.ModelAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'id', 'name', 'studio', 'get_status_display', 'get_default_schedule', 'created_by', 'created_at', 'updated_by', 'updated_at'
    )

    # CHG
    fieldsets = (
        (
            '기본 정보', {'fields': ('name', 'studio', 'status')}
        ),
        (
            '작성자', {'fields': ('created_by', 'updated_by')}
        )
    )

    def get_default_schedule(self, obj):
        return ', '.join(
            [schedule.get_day_of_week_display() + '-' + str(schedule.lesson_time) for schedule in obj.memberdefaultschedule_set.all()]
        )


class MemberDefaultScheduleAdmin(ImportExportMixin, admin.ModelAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'id', 'member', 'get_day_of_week_display', 'lesson_time', 'created_by', 'created_at', 'updated_by', 'updated_at'
    )

    pass


class MembershipAdmin(ImportExportMixin, admin.ModelAdmin):
    # 화면에 출력되는 컬럼 리스트
    list_display = (
        'id', 'member', 'reg_date', 'reg_amount', 'payment_method', 'reg_seq', 'number_of_lesson', 'created_by', 'created_at', 'updated_by', 'updated_at'
    )

    pass


admin.site.register(Studio, StudioAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(MemberDefaultSchedule, MemberDefaultScheduleAdmin)
admin.site.register(Membership, MembershipAdmin)
